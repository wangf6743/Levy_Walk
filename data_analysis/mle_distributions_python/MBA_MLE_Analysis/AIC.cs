// Calculate AIC and Aikaike weights from log-likelihoods
//	Each call to computeAIC calculates an AIC and stores an AIC min value
//	which can then be used in calls to computeWeights
//	This class only works with two models and assumtions are made about the numbers of parameters 
using System;

namespace MBA_MLE_Analysis
{
	public class AIC
	{
		private double	AIC1,
						AIC2,
						AICmin = Double.MaxValue,
						W1, W2, n;
		
		private int		K1 = 2, K2 = 2;
		
		// Constructor
		public AIC(int p_n, int D1, int D2)
		{
			n = (double) p_n;
			
			// Overide number of parameters when TP or TE is used
			if (D1 == MLE_Random.TruncatedPareto || D1 == MLE_Random.TruncatedExponential) K1 = 3;
            if (D2 == MLE_Random.TruncatedPareto || D2 == MLE_Random.TruncatedExponential) K2 = 3;
		}
										 
		public double computeAIC(double p_llh, int p_K)
		{
			double AIC;
			double K = (double)p_K; 
			
			//AIC = -2.0 * p_llh + (2.0 * K);
			AIC = -2.0 * p_llh + (2.0 * K + (2.0 * K *(K + 1))/(n - K - 1.0));
			
			if (AIC < AICmin) AICmin = AIC;
			
			return AIC;
		}
		
		public void computeWeights(double p_llh1, double p_llh2)
		{
			double DAIC1, DAIC2, sum;
			
			AIC1 = computeAIC(p_llh1, K1);
			AIC2 = computeAIC(p_llh2, K2);
	
			// Compute Weights
			DAIC1 = AIC1 - AICmin;
			DAIC2 = AIC2 - AICmin;
			sum = Math.Exp(-0.5 * DAIC1) + Math.Exp(-0.5 * DAIC2);
			
			W1 = Math.Exp(-0.5 * DAIC1) / sum;
			W2 = Math.Exp(-0.5 * DAIC2) / sum;
		}
		
		
		// Accessors
		public double getW1() {return(W1);}
		public double getW2() {return(W2);}
	}
}
