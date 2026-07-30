// Perform a test for the MLE analysis
//	This class is used during calculation of the p-value.  A synthetic data set is created and is tested by
//	MLE_Xmin/MLE_Xmax which, in the process of determining the best fit, calculates a D statistic.  It is this that will be
//	compared to the D statistic derived from the empirical data set to determine the p-value
using System;

namespace MBA_MLE_Analysis
{
	public class MLE_Calc
	{
		private int			testDSize,
							TestDist;
        private double[]    testD;					// The test array
        private	MLE_Xmin	MyMLE_Xmin;				// Xmin calculator
		private	MLE_Xmax	MyMLE_Xmax;				// Xmax calculator
		private	double		D, Xmin, Alpha, Xmax;
        private PointD      TwoP;
	
			
		public MLE_Calc(int p_testDSize, int p_TestDist, double p_Xmin, double p_Alpha, double p_Xmax, PointD p_Gamma)
		{
			testDSize = p_testDSize;
			TestDist = p_TestDist;
			Xmin = p_Xmin;
			Alpha = p_Alpha;
			Xmax = p_Xmax;
            if (p_Gamma != null) TwoP = new PointD(p_Gamma);
		}
		
		public void run()
		{
			// Create an array for the theoretical distribution values
			testD  = new double[testDSize];
			
			// Generate random test data using Xmin, Xmax and Alpha, 
			if		(TestDist == 0) MLEX.getPowerData(testD, Alpha, Xmin);
			else if (TestDist == 1) MLEX.getExponentialData(testD, Alpha, Xmin);
			else if (TestDist == 2)	MLEX.getTruncatedParetoData(testD, Alpha, Xmin, Xmax);
            else if (TestDist == 3) MLEX.getTruncatedExponentialData(testD, Alpha, Xmin, Xmax);
            else if (TestDist == 4) MLEX.getGammaData(testD, TwoP, Xmin, Xmax);
			
			// Sort the array
			Array.Sort(testD);
			
			// Use the MLE estimators to find best fit parameters for the synthetic data
			//	and as a consequence derive a GOF value
            if (TestDist <= 1 || TestDist == 4 || TestDist == 5) 
			{
				MyMLE_Xmin = new MLE_Xmin();
				MyMLE_Xmin.Run(testD, TestDist, Xmax);
				D = MyMLE_Xmin.getD();
			}
			
			// Or, for truncated Pareto or expoential, do both Xmin & Xmax
			else
			{
				// First do Xmin fitting
				MyMLE_Xmin = new MLE_Xmin();
				MyMLE_Xmin.Run(testD, TestDist, Xmax);
			
				// Get the Xmin value
				Xmin = MyMLE_Xmin.getXmin();
					
				// Now that a value has been derived for Xmin trim the steps array
				testD = MLEX.trim(testD, Xmin, Xmax);
	
				// Calculate the best fit Xmax
				MyMLE_Xmax = new MLE_Xmax();
				MyMLE_Xmax.Run(Parameters.MLE_Dist, testD, Xmin);
				D = MyMLE_Xmax.getD();
			}
		}
		
		// Member variable access methods
		public double	getD()	{return D;}
	}
}
