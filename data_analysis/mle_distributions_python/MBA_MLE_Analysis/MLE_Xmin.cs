// To estimate the best fit value for Xmin, for a given value of Alpha (mu)
//	This version copies the approach used by Clauset in that all values from the empirical
//	data are tested as possible Xmin candidates

// Xmin calculations are performed only for Power & Exponential distributions
	
using System;
using System.IO;

namespace MBA_MLE_Analysis
{
	public class MLE_Xmin
	{
		private double[]	testS, testD;
		private double		Alpha,
							BestAlpha,
							Xmin,
							BestD = Double.MaxValue,
							BestXmin,
							D;
        private PointD      TwoP,
                            BestTwoP;
		private	int			WorseCount = 0;
		
		public MLE_Xmin() {}
		public void Run(double[] p_steps, int p_TestDist, double p_Xmax)
		{
			Xmin = 0;

			// Test each unique value in steps[], until D gets worse
			for (int x = 0; x < p_steps.Length; x++)
			{
				if (p_steps[x] > Xmin)
				{
					Xmin = p_steps[x];
					
					// Create a test array that holds only steps >= Xmin
					testS = MLEX.trim(p_steps, Xmin, p_Xmax);
	
					// Using this value of Xmin calculate a new value for Alpha
					if (p_TestDist == MLE_Random.Power)						Alpha = MLEX.Power_MLE(testS, Xmin);
					else if (p_TestDist == MLE_Random.Exponential)			Alpha = MLEX.Exponential_MLE(testS, Xmin);
					else if (p_TestDist == MLE_Random.TruncatedPareto)		Alpha = MLEX.TrucatedPareto_MLE(testS, Xmin, p_Xmax);
					else if (p_TestDist == MLE_Random.TruncatedExponential) Alpha = MLEX.TruncatedExponential_MLE(testS, Xmin, p_Xmax);
                    else if (p_TestDist == MLE_Random.TruncatedExponential) Alpha = MLEX.TruncatedExponential_MLE(testS, Xmin, p_Xmax);
                    else if (p_TestDist == MLE_Random.Gamma)                TwoP = MLEX.Gamma_MLE(testS);
                    else if (p_TestDist == MLE_Random.LogNormal)            TwoP = MLEX.LogNormal_MLE(testS);
	
					// Create an array for the theoretical distribution values
					testD  = new double[testS.Length];
	
					// Populate testD[] with good values from the proposed distribution and the Xmin and Alpha values just derived
					//	Note that this generates a non-random distribution, as does the Clauset Matlab KS test 
					if (p_TestDist == MLE_Random.Power)						MLEX.getGoodPowerData(testD, Alpha, Xmin);
					else if (p_TestDist == MLE_Random.Exponential)			MLEX.getGoodExponentialData(testD, Alpha, Xmin);
					else if (p_TestDist == MLE_Random.TruncatedPareto)		MLEX.getGoodTruncatedParetoData(testD, Alpha, Xmin, p_Xmax);
					else if (p_TestDist == MLE_Random.TruncatedExponential) MLEX.getGoodTruncatedExponentialData(testD, Alpha, Xmin, p_Xmax);
                    else if (p_TestDist == MLE_Random.Gamma)                MLEX.getGoodGammaData(testD, TwoP, Xmin, p_Xmax);
                    else if (p_TestDist == MLE_Random.LogNormal)            MLEX.getGoodLogNormalData(testD, TwoP, Xmin, p_Xmax);
				
					// Do a KS test
					D = GOF.Kolmogorov_Smirnov(testS, testD, false, false);

					// Adjust D for range of data fitted, if Best fit Xmin option selected
					if (Parameters.MLE_Fitting == 2)
					{
						D = D * (Math.Log(p_steps.Length) / Math.Log(testS.Length));
					}
	
					// If D is < Best D then store D, Alpha and Xmin
					if (D < BestD) 
					{
						BestD = D;			// Store best D
						BestXmin = Xmin;	// Store best Xmin
						BestAlpha = Alpha;	// Store best Alpha

                        if (p_TestDist == MLE_Random.Gamma || p_TestDist == MLE_Random.LogNormal) BestTwoP = new PointD(TwoP);

						WorseCount = 0;
					}
					else 
					{
						WorseCount++;
					}
				}
				
				if (Parameters.MLE_Fitting != 2 && WorseCount > Parameters.MLE_WorseCount) break;
			}
		}
	
		// Member variable access functions
		public double	getXmin()		{return BestXmin;}
		public double	getAlpha()		{return BestAlpha;}
		public double	getD()			{return BestD;}
        public PointD  getTwoP()        { return BestTwoP; }
	}
}
