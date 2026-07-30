// This class : the Maximum Likelihood Estimators for the Power law Exponential and Truncated Pareto distributions 
//	as described in the Aaron Clauset paper "Power-law distributions in Empirical data" and others

//	For details on Power and Exponential estimators & log-likelihoods see Aaron Clauset Power-law distributions in empirical data
//		(http://arxiv.org/abs/0706.1062v1)

//	Also, see Ethan P. White, Brian J. Enquist, and Jessica L. Green. 2008. 
//				On estimating the exponents of power-law frequency distributions. Ecology 89:905-912.
//				Appendix A in supplementary information

//	Also, for Truncated Pareto equations see Kagan 2002 (Geophys. J. Int. (2002) 148, 520�541)

using System;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{
	public class MLE
	{
		private	Writer		MyWriter;
	    private string		FileID, Output;
		private	MLE_Calc[]	MyMLE_Calc;
		private Thread[]	MyMLE_Threads;
		private MLE_Xmin	MyMLE_Xmin;
		private	MLE_Xmax	MyMLE_Xmax;
		private	AIC			MyAIC;
		
		private double		Xmin,				// Empirical Xmin & D values
							Xmax,				// Maximum for Truncated power law (Truncated Pareto distribution)
							Alpha,
							D,					// The K-S D (GOF) statistic
							GtD,
							p,
							AltAlpha,			// Exponential exponent fitted to reduced TP or P data set 
							AltGOF,				//  KS test result for the above
							AltLLH,				//	LLH for above
							LLH,				// Log-likelihood
							AICw,				// Akaike weight for test distribution 
							AltAICw;			//	and exponential fitted to reduced data set

        private PointD      TwoP,               // To hold parameters for two parameter distributions
                            AltTwoP;

		private double[]	steps,				// Step data from the track 
							TSteps,				// Truncated steps, using Xmin & Xmax
							AltSteps,			// For the alternate test
							GoodSteps;			// Arrays of real steps from the best fit distribution
		
		private	int			NoOfTests,			// Number of Monte Carlo tests to perform
							testDSize,			// Size of the test distribution
							x,					// Indicies
							ax,
							gx,
                            CPUs,
							rank;
		
		private Label		l_Exp,
							l_Xmin,
							l_Xmax,
							l_GOF,
							l_Alt_GOF,
							l_KSp,
							l_AICw,
							l_Alt_AICw;

		public bool			OK = false;
		
		// The constructor does nothing
		public MLE() {}

		// Perform the analysis
		//	This method should be shared between track and dive analysis
		public void Run(Track p_Track, Graph p_Graph, Form1 p_Form1, bool p_Quick)
		{	
			// Initialise variables
			GtD = 0;

			// Store option settings
			CPUs = Environment.ProcessorCount;
			
			// Set up label pointers according to the selected distribution
			SetLabels(p_Form1);
			
			// Clear labels
			l_Exp.Text = ""; 
			l_Xmin.Text = ""; 
			l_GOF.Text = ""; 
			l_Alt_GOF.Text = ""; 
			l_KSp.Text = ""; 
			l_AICw.Text = ""; 
			l_Alt_AICw.Text = "";
			l_Xmax.Text = "";
	
			// Prompt for the output file
			if (!p_Quick)
			{
				// Set up the output file name to reflect the analysis being performed
				SetFileName();
				MyWriter = new Writer(p_Track, "MLE analysis", FileID);
				
				if (!MyWriter.IsOK()) return;
			}
			
			// Set MLEX Discrete flag
			//	This is kept separate because of the need to override it later on to generate Real 
			//	distributions regardless of how this is set.
			MLEX.setDiscrete(Parameters.MLE_Discrete);
	
			// Create the array of non-zero values
			p_Form1.l_Status.Text = "Extracting step lengths...";
			Application.DoEvents();

			steps = p_Track.getSteps(); 
			p_Form1.l_Coalesed.Text = p_Track.CoalesedSteps.ToString();
			p_Form1.l_Gaps.Text = p_Track.IgnoredTrackGaps.ToString();
			Application.DoEvents();
			
			// Exit if no steps
			if (steps.Length < 1) return;
			
			// Sort the steps array ready for the rest of the processing
			Array.Sort(steps);
			
			// Get initial Xmin & Xmax values
			Xmin = steps[0];
			Xmax = steps[steps.Length - 1];

			l_Xmin.Text = Parameters.RoundD(Xmin);
			
			if (Parameters.MLE_Dist >= 2) l_Xmax.Text = Parameters.RoundD(Xmax);
			
			Application.DoEvents();
					
			// Store the Xmin value (for discrete conversion)
			MLEX.setXmin(Xmin);
			
			// Use an MLE to calculate a best fit value for Alpha (mu)
			//	NOTE we do this to give a first guess regardless of the analysis options selected
			//	Start with a trial Xmin/Xmax calculated from the data
			//	NOTE: This is not really neccessary as it is done at the start of the MLE_Xmin search,
			//		however it does give quick feedback and, more importantly, it indicates whether the Xmin search actually
			//		improves on the first values found.  It is also needed if NoFit is set of course
			if		(Parameters.MLE_Dist == 0)	Alpha = MLEX.Power_MLE(steps, Xmin);
			else if (Parameters.MLE_Dist == 1)	Alpha = MLEX.Exponential_MLE(steps, Xmin);
			else if (Parameters.MLE_Dist == 2)  Alpha = MLEX.TrucatedPareto_MLE(steps, Xmin, Xmax);
			else if (Parameters.MLE_Dist == 3)  Alpha = MLEX.TruncatedExponential_MLE(steps, Xmin, Xmax);
            else if (Parameters.MLE_Dist == 4)  TwoP = MLEX.Gamma_MLE(steps);
            else if (Parameters.MLE_Dist == 5)  TwoP = MLEX.LogNormal_MLE(steps);
	
			// Update labels
            if (Parameters.MLE_Dist == 4 || Parameters.MLE_Dist == 5)   l_Exp.Text = TwoP.X.ToString("F2") + " / " + TwoP.Y.ToString("F2");
            else                            l_Exp.Text = Alpha.ToString("F3");

			p_Form1.l_Status.Text = "Estimating Xmin...";
			Application.DoEvents();
			
			// If no fitting is required then generate a best fit data set and do a KS test to get a GOF 
			if (Parameters.MLE_Fitting == 1)
			{
				TSteps = new double[steps.Length];
				
				if		(Parameters.MLE_Dist == 0) MLEX.getGoodPowerData(TSteps, Alpha, Xmin);
				else if (Parameters.MLE_Dist == 1) MLEX.getGoodExponentialData(TSteps, Alpha, Xmin);
				else if (Parameters.MLE_Dist == 2) MLEX.getGoodTruncatedParetoData(TSteps, Alpha, Xmin, Xmax);
                else if (Parameters.MLE_Dist == 3) MLEX.getGoodTruncatedExponentialData(TSteps, Alpha, Xmin, Xmax);
                else if (Parameters.MLE_Dist == 4) MLEX.getGoodGammaData(TSteps, TwoP, Xmin, Xmax);
                else if (Parameters.MLE_Dist == 5) MLEX.getGoodLogNormalData(TSteps, TwoP, Xmin, Xmax);
				
				// Do a KS test
				D = GOF.Kolmogorov_Smirnov(steps, TSteps, false, false);
			}
			
			// Fit the data to calculate Xmin, Xmax
			// Use the MLE estimators to find best fit values for the Xmin and Xmax parameters
			else
			{
				// Find a best fit value for Xmin for Power or exponential etc.
				if (Parameters.MLE_Dist <= 1 || Parameters.MLE_Dist == MLE_Random.Gamma || Parameters.MLE_Dist == MLE_Random.LogNormal) 
				{
					MyMLE_Xmin = new MLE_Xmin();
					MyMLE_Xmin.Run(steps, Parameters.MLE_Dist, Xmax);
			
					// Having found the best fit value for Xmin collect the best fit values for Alpha and the goodness of fit (D)
					D = MyMLE_Xmin.getD();
					Xmin = MyMLE_Xmin.getXmin();
					Alpha = MyMLE_Xmin.getAlpha();

                    if (Parameters.MLE_Dist == MLE_Random.Gamma || Parameters.MLE_Dist == MLE_Random.LogNormal)
                    {
                        TwoP = MyMLE_Xmin.getTwoP();
                    }
                }
			
				// For truncated Pareto or truncated exponential, do both Xmin and Xmax
				else if (Parameters.MLE_Dist == 2 || Parameters.MLE_Dist == 3) 
				{
					// First do Xmin fitting 
					MyMLE_Xmin = new MLE_Xmin();
					MyMLE_Xmin.Run(steps, Parameters.MLE_Dist, Xmax);
			
					// Having found the best fit value for Xmin collect the best fit values for Alpha and the goodness of fit (D)
					Xmin = MyMLE_Xmin.getXmin();
							
					// Now that a value has been derived for Xmin trim the steps array
					TSteps = MLEX.trim(steps, Xmin, Xmax);
		
					// Calculate the best fit Xmax
					MyMLE_Xmax = new MLE_Xmax();
					MyMLE_Xmax.Run(Parameters.MLE_Dist, TSteps, Xmin);
		
					// Having found the best fit value for Xmax collect the best fit values for Alpha and the goodness of fit (D)
					D = MyMLE_Xmax.getD();
					Alpha = MyMLE_Xmax.getAlpha();
					Xmax = MyMLE_Xmax.getXmax();
				}
			}
	
			// Update labels with the fitted estimates
            if (Parameters.MLE_Dist == 4 
                || Parameters.MLE_Dist == 5)   l_Exp.Text = TwoP.X.ToString("F2") + " / " + TwoP.Y.ToString("F2");
            else                               l_Exp.Text = Alpha.ToString("F3");

            l_Xmin.Text = Parameters.RoundD(Xmin);

			if (Parameters.MLE_Dist == 2 || Parameters.MLE_Dist == 3) l_Xmax.Text = Parameters.RoundD(Xmax);
			
			l_GOF.Text = D.ToString("F3");
			Application.DoEvents();
			
			// Now that values have been derived for Xmin & Xmax trim the steps array
			TSteps = MLEX.trim(steps, Xmin, Xmax);
	
			// Calculate the LLH
            if      (Parameters.MLE_Dist == 0) LLH = MLEX.Power_LLH(TSteps, Alpha, Xmin);
            else if (Parameters.MLE_Dist == 1) LLH = MLEX.Exponential_LLH(TSteps, Alpha, Xmin);
            else if (Parameters.MLE_Dist == 2) LLH = MLEX.TP_LLH(TSteps, Alpha, Xmin, Xmax);
            else if (Parameters.MLE_Dist == 3) LLH = MLEX.TE_LLH(TSteps, Alpha, Xmin, Xmax);
            else if (Parameters.MLE_Dist == 4) LLH = MLEX.Gamma_LLH(TSteps, TwoP.X, TwoP.Y);
            else if (Parameters.MLE_Dist == 5) LLH = MLEX.LogNormal_LLH(TSteps, TwoP.X, TwoP.Y);

			// To check whether the estimated Alpha and Xmin values do describe a distribution that matches the observations
			//	it is neccessary to generate n sets of synthetic data using these parameters and count the number 
			//	where the computed D statistic > the empirical D statistic.  This can then be used to compute a p-value
			if (Parameters.MLE_p_Test) pTest(p_Form1, p_Quick);
			
			// Calculate GOF, LLH and wAIC values for the selected alternate distribution
			// Calculate mu or lambda
            if (Parameters.MLE_AltDist == 0)      AltAlpha = MLEX.Power_MLE(TSteps, Xmin);
            else if (Parameters.MLE_AltDist == 1) AltAlpha = MLEX.Exponential_MLE(TSteps, Xmin);
            else if (Parameters.MLE_AltDist == 2) AltAlpha = MLEX.TrucatedPareto_MLE(TSteps, Xmin, Xmax);
            else if (Parameters.MLE_AltDist == 3) AltAlpha = MLEX.TruncatedExponential_MLE(TSteps, Xmin, Xmax);
            else if (Parameters.MLE_AltDist == 4) AltTwoP = MLEX.Gamma_MLE(TSteps);
            else if (Parameters.MLE_AltDist == 5) AltTwoP = MLEX.LogNormal_MLE(TSteps);

            // We need to set this, as it controls how things are displayed
            if (Parameters.MLE_AltDist == 4 || Parameters.MLE_AltDist == 5) AltAlpha = AltTwoP.X;
            	
			// If AltAlpha is zero then something has gone wrong with the alternate distribution MLE
			//	Report the error
			if (AltAlpha == 0)
			{
				MessageBox.Show("Warning. MLE has failed for the alternate distribution.\nAkaike weights have not been computed and a plot has not been produced."
								, "MLE warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
			}

			// Generate a good alternate data set
            if (AltAlpha != 0.0)
			{
				AltSteps = new double[TSteps.Length];

				if (Parameters.MLE_AltDist == 0) MLEX.getGoodPowerData(AltSteps, AltAlpha, Xmin);
				else if (Parameters.MLE_AltDist == 1) MLEX.getGoodExponentialData(AltSteps, AltAlpha, Xmin);
				else if (Parameters.MLE_AltDist == 2) MLEX.getGoodTruncatedParetoData(AltSteps, AltAlpha, Xmin, Xmax);
				else if (Parameters.MLE_AltDist == 3) MLEX.getGoodTruncatedExponentialData(AltSteps, AltAlpha, Xmin, Xmax);
                else if (Parameters.MLE_AltDist == 4) MLEX.getGoodGammaData(AltSteps, AltTwoP, Xmin, Xmax);
                else if (Parameters.MLE_AltDist == 5) MLEX.getGoodLogNormalData(AltSteps, AltTwoP, Xmin, Xmax);

				// Perform the KS test
				AltGOF = GOF.Kolmogorov_Smirnov(TSteps, AltSteps);
				l_Alt_GOF.Text = AltGOF.ToString("F3");

				// Calculate the LLH of the alternate, given the original data
				if (Parameters.MLE_AltDist == 0) AltLLH = MLEX.Power_LLH(TSteps, AltAlpha, Xmin);
				else if (Parameters.MLE_AltDist == 1) AltLLH = MLEX.Exponential_LLH(TSteps, AltAlpha, Xmin);
				else if (Parameters.MLE_AltDist == 2) AltLLH = MLEX.TP_LLH(TSteps, AltAlpha, Xmin, Xmax);
                else if (Parameters.MLE_AltDist == 3) AltLLH = MLEX.TE_LLH(TSteps, AltAlpha, Xmin, Xmax);
                else if (Parameters.MLE_AltDist == 4) AltLLH = MLEX.Gamma_LLH(TSteps, AltTwoP.X, AltTwoP.Y);
                else if (Parameters.MLE_AltDist == 5) AltLLH = MLEX.LogNormal_LLH(TSteps, AltTwoP.X, AltTwoP.Y);

				// Now calculate Aikaike weights, if the LLH values are valid
				if (LLH != 0 && AltLLH != 0 && TSteps.Length > 4)
				{
					MyAIC = new AIC(TSteps.Length, Parameters.MLE_Dist, Parameters.MLE_AltDist);
					MyAIC.computeWeights(LLH, AltLLH);
					AICw = MyAIC.getW1();
					AltAICw = MyAIC.getW2();

					// Update labels
					l_AICw.Text = AICw.ToString("F3");
					l_Alt_AICw.Text = AltAICw.ToString("F3");
				}
				else
				{
					String msg;

					if (TSteps.Length < 5) msg = "There are fewer than 5 fitted steps available for analysis";
					else msg = "Loglikelihood calculation has failed";

					MessageBox.Show(msg, "MLE warning, AIC not computed", MessageBoxButtons.OK, MessageBoxIcon.Warning);
				}
			}

			Application.DoEvents();
			
			// Clear the discrete flag so that REAL distributions can be generatated for output
			if (MLEX.Discrete)
			{
				MLEX.setDiscrete(false);

				// Recreate the alternate distribution
				if (Parameters.MLE_AltDist == 0)	  MLEX.getGoodPowerData(AltSteps, AltAlpha, Xmin);
				else if (Parameters.MLE_AltDist == 1) MLEX.getGoodExponentialData(AltSteps, AltAlpha, Xmin);
				else if (Parameters.MLE_AltDist == 2) MLEX.getGoodTruncatedParetoData(AltSteps, AltAlpha, Xmin, Xmax);
				else if (Parameters.MLE_AltDist == 3) MLEX.getGoodTruncatedExponentialData(AltSteps, AltAlpha, Xmin, Xmax);
                else if (Parameters.MLE_AltDist == 4) MLEX.getGoodGammaData(AltSteps, AltTwoP, Xmin, Xmax);
                else if (Parameters.MLE_AltDist == 5) MLEX.getGoodLogNormalData(AltSteps, AltTwoP, Xmin, Xmax);
            }
								
			GoodSteps = new double[TSteps.Length];
			
			if		(Parameters.MLE_Dist == 0) MLEX.getGoodPowerData(GoodSteps, Alpha, Xmin);
			else if (Parameters.MLE_Dist == 1) MLEX.getGoodExponentialData(GoodSteps, Alpha, Xmin);
			else if (Parameters.MLE_Dist == 2) MLEX.getGoodTruncatedParetoData(GoodSteps, Alpha, Xmin, Xmax);
			else if (Parameters.MLE_Dist == 3) MLEX.getGoodTruncatedExponentialData(GoodSteps, Alpha, Xmin, Xmax);
            else if (Parameters.MLE_Dist == 4) MLEX.getGoodGammaData(GoodSteps, TwoP, Xmin, Xmax);
            else if (Parameters.MLE_Dist == 5) MLEX.getGoodLogNormalData(GoodSteps, TwoP, Xmin, Xmax);
			
			OK = true;

			// Perform output
			WriteOutput(p_Track, p_Graph, p_Quick);
		}

		// Perform pTest calculations
		private void pTest(Form1 p_Form1, bool p_Quick)
		{
			// Set required number of tests
			if (p_Quick) NoOfTests = 1000;
			else NoOfTests = 2500;

			// Set up progress bar
			p_Form1.pb_Progress.Maximum = NoOfTests / CPUs;
			p_Form1.pb_Progress.Step = 1;
			p_Form1.pb_Progress.Value = 0;

			p_Form1.l_Status.Text = "Performing p-value calculations...";
			Application.DoEvents();
			
			// Set the size of the test data to match the length of the trimmed observed data
			testDSize = TSteps.Length;

			// Run the required number of tests
			MyMLE_Calc = new MLE_Calc[CPUs];
			MyMLE_Threads = new Thread[CPUs];

			for (int t = 0; t < NoOfTests; t += CPUs)
			{
				Application.DoEvents();

				for (int cpu = 0; cpu < CPUs; cpu++)
				{
					if (t + cpu < NoOfTests)
					{
						MyMLE_Calc[cpu] = new MLE_Calc(testDSize, Parameters.MLE_Dist, Xmin, Alpha, Xmax, TwoP);
						MyMLE_Threads[cpu] = new Thread(MyMLE_Calc[cpu].run);
						MyMLE_Threads[cpu].Start();
					}
				}

				// Collect the results
				for (int cpu = 0; cpu < CPUs; cpu++)
				{
					if (MyMLE_Calc[cpu] != null)
					{
						if (MyMLE_Threads[cpu] != null)
						{
							try { MyMLE_Threads[cpu].Join(); }
							catch (Exception) { }

							if (MyMLE_Calc[cpu].getD() > D) GtD++;
							MyMLE_Calc[cpu] = null;
						}
					}
				}

				// Update progress bar	
				p_Form1.pb_Progress.PerformStep();
				Application.DoEvents();
			}

			// Calculate p from the number of tests passed
			if (NoOfTests > 0) p = (double)GtD / (double)NoOfTests;

			// Update labels 
			p_Form1.pb_Progress.Value = 0;
			l_KSp.Text = p.ToString("F3");
			Application.DoEvents();
		}

		// Perform output
		private void WriteOutput(Track p_Track, Graph p_Graph, bool p_Quick)
		{
			// Populate the graph with rank step-length data
			if (p_Quick)
			{
				// Set up the graph
				p_Graph.set_Size(steps.Length);
				
				// Set starting indices
				rank = 0;
				gx = GoodSteps.Length - 1;

                if (AltAlpha != 0) ax = AltSteps.Length - 1;

				// Write graph data for a rank step-length plot
				//	Note that output of TP data will be delayed until Xmax is reached
				for (x = steps.Length - 1; x >= 0; x--)
				{
					p_Graph.add_Point(Math.Log10(steps[x]), Math.Log10(++rank));

					if (steps[x] <= Xmax)
					{
						if (gx >= 0) p_Graph.add_Point2(Math.Log10(GoodSteps[gx--]), Math.Log10(rank));
						if (AltAlpha != 0.0 && ax >= 0) p_Graph.add_Point3(Math.Log10(AltSteps[ax--]), Math.Log10(rank));
					}
				}

				return;
			}

			// Write MLE details
			MyWriter.WriteLine("Maximum Likelihood Estimation analysis details");
			MyWriter.WriteLine("");

			// Write selected dimension
			if (Track.XY_Data)
			{
				if (Parameters.MLE_Dimension == 0) MyWriter.WriteLine("X dimension selected");
				else if (Parameters.MLE_Dimension == 0) MyWriter.WriteLine("Y dimension selected");
				else MyWriter.WriteLine("Z dimension selected");
				MyWriter.WriteLine("");
			}
			else if (Track.LatLon_Data)
			{
				if (Parameters.MLE_Dimension == 0) MyWriter.WriteLine("Longitude selected");
				else MyWriter.WriteLine("Latitude selected");
				MyWriter.WriteLine("");
			}
			else if (Track.Step_Data)
			{
				MyWriter.WriteLine("Steps processed");
				MyWriter.WriteLine("");
			}
			else
			{
				MyWriter.WriteLine("Depths processed");
				MyWriter.WriteLine("");
			}
			
			MyWriter.WriteLine("Number of coalesed steps," + p_Track.CoalesedSteps.ToString());
			MyWriter.WriteLine("Number of ignored gaps," + p_Track.IgnoredTrackGaps.ToString());
			MyWriter.WriteLine("Steps < Xmin or > Xmax," + p_Track.ZeroSteps.ToString());
			MyWriter.WriteLine("");

			if (Parameters.MLE_p_Test)
			{
				MyWriter.WriteLine("No of Tests for p-value calculation," + NoOfTests.ToString()
								+ ",Data set size," + testDSize.ToString());
				MyWriter.WriteLine("");
			}

			Output = steps.Length.ToString();

			if (Parameters.MLE_Discrete) Output = Output + " Discrete ";
			else Output = Output + " Real ";

			if (Parameters.MLE_Type == 0) Output = Output + " Step lengths ";
			else if (Parameters.MLE_Type == 1) Output = Output + " Step lengths ";
			else if (Parameters.MLE_Type == 2) Output = Output + " Activity times ";
			else if (Parameters.MLE_Type == 3) Output = Output + " Mean Activity times ";

			Output = Output + "used (Trimmed to " + TSteps.Length.ToString() + ")";
			MyWriter.WriteLine(Output);

			// Write fitting option
			MyWriter.WriteLine("");

			if (Parameters.MLE_Fitting == 0) MyWriter.WriteLine("Limited fitting of Xmin and Xmax");
			else if(Parameters.MLE_Fitting == 1) MyWriter.WriteLine("No fitting of Xmin and Xmax");
			else MyWriter.WriteLine("Best fit found for Xmin from all possible values");

			if (Parameters.MLE_Xmin > 0 || Parameters.MLE_Xmax > 0)
			{
				MyWriter.WriteLine("Initial Xmin set to," + Parameters.MLE_Xmin.ToString("F2") + ",Initial Xmax set to," + Parameters.MLE_Xmax.ToString("F2"));
				MyWriter.WriteLine("");
			}

			if (Parameters.MLE_Dist == 0)      Output = "Power law,Exponent,";
			else if (Parameters.MLE_Dist == 1) Output = "Exponential,Exponent,";
			else if (Parameters.MLE_Dist == 2) Output = "Truncated Pareto,Exponent,";
            else if (Parameters.MLE_Dist == 3) Output = "Truncated Exponential,Exponent,";
            else if (Parameters.MLE_Dist == 4) Output = "Gamma,Shape (k) : Rate,";
            else if (Parameters.MLE_Dist == 5) Output = "Log Normal,Mean : S.D.,";

            if (Parameters.MLE_Dist < 4)
            {
                Output = Output + Alpha.ToString("F4") + ",Xmin," + Xmin.ToString("F4");
            }
            else
            {
                Output = Output + TwoP.X.ToString("F4") + " : " + TwoP.Y.ToString("F4") + ",,";
            }

			if (Parameters.MLE_Dist == 2 || Parameters.MLE_Dist == 3) Output = Output + ",Xmax," + Xmax.ToString();
          
            Output = Output + ",GOF," + D.ToString("F4")
							+ ",LLH," + LLH.ToString("F4")
							+ ",wAIC," + AICw.ToString("F4")
							+ ",p-value," + p.ToString("F4");
			MyWriter.WriteLine(Output);

			// Write alternate distribution details
			if (Parameters.MLE_AltDist == 0) Output = "Power law,Exponent,";
			else if (Parameters.MLE_AltDist == 1) Output = "Exponential,Exponent,";
			else if (Parameters.MLE_AltDist == 2) Output = "Truncated Pareto,Exponent,";
            else if (Parameters.MLE_AltDist == 3) Output = "Truncated Exponential,Exponent,";
            else if (Parameters.MLE_AltDist == 4) Output = "Gamma,Shape (k) : Rate,";
            else if (Parameters.MLE_AltDist == 5) Output = "Log Normal,Mean : S.D.,";

			if (Parameters.MLE_AltDist < 4)
			{
				Output = Output + AltAlpha.ToString("F4");
			}
			else
			{
				Output = Output + AltTwoP.X.ToString("F4") + " : " + AltTwoP.Y.ToString("F4");
			}

			// We don't need Xmin & Xmax cause they are the same
			if (Parameters.MLE_Dist == 2 | Parameters.MLE_Dist == 3) Output = Output + ",,";

			Output = Output + ",,,GOF," + AltGOF.ToString("F4")
							+ ",LLH," + AltLLH.ToString("F4")
							+ ",wAIC," + AltAICw.ToString("F4");
			MyWriter.WriteLine(Output);

			// Write column headings
			MyWriter.WriteLine("");
			MyWriter.WriteLine("log10(Rank),log10(Observed),log10(Best fit),log10(Alternate)");

			// Set starting indices
			rank = 0;
			gx = GoodSteps.Length - 1;
			ax = AltSteps.Length - 1;
			StringBuilder sb;

			// Write out data for the simple, plot and an RF plot
			for (x = steps.Length - 1; x >= 0; x--)
			{
				sb = new StringBuilder(Math.Log10(++rank).ToString());
				sb.Append(",");
				sb.Append(Math.Log10(steps[x]).ToString());

				if (steps[x] <= Xmax)
				{
					sb.Append(",");
					if (gx >= 0) sb.Append(Math.Log10(GoodSteps[gx--]).ToString());
					sb.Append(",");
					if (ax >= 0) sb.Append(Math.Log10(AltSteps[ax--]).ToString());
				}

				MyWriter.WriteLine(sb.ToString());
			}

			// Close the file
			MyWriter.Close();
			return;
		}

		// Set up the output file name to reflect the analysis being performed
		private void SetFileName()
		{
			// Change file name to show test
			if (Parameters.MLE_Dist == 0) FileID = "MLE (P";
			else if (Parameters.MLE_Dist == 1) FileID = "MLE (E";
			else if (Parameters.MLE_Dist == 2) FileID = "MLE (TP";
			else if (Parameters.MLE_Dist == 3) FileID = "MLE (TE";
			else if (Parameters.MLE_Dist == 4) FileID = "MLE (G";
			else if (Parameters.MLE_Dist == 5) FileID = "MLE (LN";

			// and alternate test
			if (Parameters.MLE_AltDist == 0) FileID = FileID + "-P)";
			else if (Parameters.MLE_AltDist == 1) FileID = FileID + "-E)";
			else if (Parameters.MLE_AltDist == 2) FileID = FileID + "-TP)";
			else if (Parameters.MLE_AltDist == 3) FileID = FileID + "-TE)";
			else if (Parameters.MLE_AltDist == 4) FileID = FileID + "-G)";
			else if (Parameters.MLE_AltDist == 5) FileID = FileID + "-LN)";
		}

		// Set up pointers to the output labels to be used
		//	This code differs between track & dive analysis
		private void SetLabels(Form1 p_Form1)
		{
			// There is only one set of output labels in this version
			l_Exp = p_Form1.l_MLE_Exponent;
			l_Xmin = p_Form1.l_MLE_Xmin;
			l_Xmax = p_Form1.l_MLE_Xmax;
			l_GOF = p_Form1.l_MLE_GOF;
			l_KSp = p_Form1.l_MLE_p;
			l_AICw = p_Form1.l_MLE_AICw;
			l_Alt_GOF = p_Form1.l_MLE_AltGOF;
			l_Alt_AICw = p_Form1.l_MLE_AltAICw;
		}
		
		// Member variable access functions
		public double getAlpha()	{return Alpha;}
		public double getp()		{return p;}
		public double getXmin()		{return Xmin;}
		public double getXmax()		{return Xmax;}
		public double getD()		{return D;}
		public double getAltGOF()	{return AltGOF;}
		public double getLLH()		{return LLH;}
		public double getAltLLH()	{return AltLLH;}
		public double getAICw()		{return AICw;}
		public double getAltAICw()	{return AltAICw;}
		public int	  getSteps()	{return TSteps.Length;}
	}
}
