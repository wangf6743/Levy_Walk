// To estimate the best fit value for Xmax, for a given value of Alpha (mu)
//	This version copies the approach used by Clauset in that all values from the empirical
//	data are tested as possible Xmax candidates

//	This method is only used for the Truncated Pareto distribution
	
using System;

namespace MBA_MLE_Analysis
{
	public class MLE_Xmax
	{
		private double[]	testS, testD;
		private double		Alpha,
							BestAlpha,
							Xmax = Double.MaxValue,
							BestD = Double.MaxValue,
							BestXmax,
							D;
		private	int			WorseCount = 0;
		
		public MLE_Xmax()
		{}
		
		public void Run(int p_TestDist, double[] p_steps, double p_Xmin)
		{
			// Test each unique value in steps[], until D gets worse
			//	Note that here we work backwards from the largest value
			for(int x = p_steps.Length - 1; x > 0; x--)
			{
				if (p_steps[x] < Xmax)
				{
					Xmax = p_steps[x];
	
					// Create a test array that holds only steps >= Xmin and <= Xmax
					testS = MLEX.trim(p_steps, p_Xmin, Xmax);
	
					// Using this value of Xmax calculate a new value for Alpha
					if (p_TestDist == MLE_Random.TruncatedPareto) Alpha = MLEX.TrucatedPareto_MLE(testS, p_Xmin, Xmax);
					else if (p_TestDist == MLE_Random.TruncatedExponential) Alpha = MLEX.TruncatedExponential_MLE(testS, p_Xmin, Xmax);
	
					// Create an array for the theoretical distribution values
					testD  = new double[testS.Length];
	
					// Populate testD[] with good values from the proposed power law and the Xmax and Alpha values just derived
					//	Note that this generates a non-random distribution, as does the Clauset Matlab KS test 
					if (p_TestDist == MLE_Random.TruncatedPareto) MLEX.getGoodTruncatedParetoData(testD, Alpha, p_Xmin, Xmax);
					else if (p_TestDist == MLE_Random.TruncatedExponential) MLEX.getGoodTruncatedExponentialData(testD, Alpha, p_Xmin, Xmax);
					
					// Do a KS test
					D = GOF.Kolmogorov_Smirnov(testS, testD, false, false);

					// Adjust D for range of data fitted
					if (Parameters.MLE_Fitting == 2)
					{
						D = D * (Math.Log(p_steps.Length) / Math.Log(testS.Length));
					}

					// If D is < Best D then store D, Alpha and Xmin
					if (D < BestD) 
					{
						BestD = D;			// Store best D
						BestXmax = Xmax;	// Store best Xmax
						BestAlpha = Alpha;	// Store best Alpha
						WorseCount = 0;
					}
					else 
					{
						WorseCount++;
					}
				}
				
				if (WorseCount > Parameters.MLE_WorseCount) break;
			}
		}
	
		// Member variable access functions
		public double	getXmax()		{return BestXmax;}
		public double	getAlpha()		{return BestAlpha;}
		public double	getD()			{return BestD;}
	}
}
