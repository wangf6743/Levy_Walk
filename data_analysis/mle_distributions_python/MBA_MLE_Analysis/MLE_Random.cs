// This class provides random number generators for Power law,
//	exponential and truncated Pareto distributions

// To use the class create an instance with the required distribution and parameters
	
using System;

namespace MBA_MLE_Analysis
{
	public class MLE_Random
	{
		public const int			Power = 0,
									Exponential = 1,
									TruncatedPareto = 2,
									TruncatedExponential = 3,
                                    Gamma = 4, 
                                    LogNormal = 5;
		
		public static string[]		Distributions = {"Power", "Exponential", "Truncated Pareto", "Truncated exponential", "Gamma", "Log Normal"};   
	
		private int		Dist;		// The distribution (as above)
		
		private	double	Exponent,
						Xmin,
						Xmax,
						PDExponent,
						EDExponent,
						beta,
						TPTerm1,
						TPTerm2,
						TPTerm3,
                        Alpha, Theta,   // For gamma
                        Mu, Sigma;      // For Normal/LogNormal

        // Stuff for the Gamma, LogNormal & Normal RNGs
        private double ND_NextVariate = 0.0, GH1, GH2;
        private bool ND_Return_Next = false;

		private Random MyRandom;
		
		// Store the parameters and set up some useful constants
		public MLE_Random (int p_Dist, double p_Exponent, double p_Xmin, double p_Xmax)
		{
			Dist = p_Dist;
			Exponent = p_Exponent;
			Xmin = p_Xmin;
			Xmax = p_Xmax;
	
			// Set up useful constants
			if (Dist == Power && Exponent != 1.0) PDExponent = -1.0 / (Exponent - 1.0);
			if (Dist == Exponential && Exponent != 0) EDExponent = 1.0 / Exponent;
			
			if (Dist == TruncatedPareto)
			{
				beta = Exponent - 1.0;
				TPTerm1 = (1.0 - Math.Pow(Xmax/Xmin, -beta));
				TPTerm2 = Math.Pow(Xmax/Xmin, -beta);
				TPTerm3 = (-1.0 / beta);
			}

			// Create the system random number generator
			MyRandom = new Random();
		}

		// Store the parameters for a Gamma/Log-normal
		public MLE_Random (int p_Dist, PointD p)
		{
			Dist = p_Dist;

            if (Dist == Gamma)
            {
                Alpha = p.X;
                Theta = p.Y;
                GH1 = Alpha - Math.Floor(Alpha);
                GH2 = Math.E / (Math.E + GH1);
            }

            else if (Dist == LogNormal)
            {
                Mu = p.X;
                Sigma = p.Y;
  
                // Initialise the log normal generator
                ND_NextVariate = 0.0;
                ND_Return_Next = false;
            }
		}
			
		// Return a random number
		public double Next()
		{
			switch (Dist)
			{
				case Power:				    return getPower();
				case Exponential:		    return getExponential();
				case TruncatedPareto:	    return getTruncatedPareto();
				case TruncatedExponential:  return getTruncatedExponential();
                case Gamma:                 return GammaNextDouble();
                default:                    return LogNormalNextDouble();
			}
		}

		//---------------------------//
		// RANDOM NUMBER GENERATORS  //
		//---------------------------//
				
		// Generate power law random number
		private double getPower()
		{	
			return Xmin * Math.Pow(1.0 - MyRandom.NextDouble(), PDExponent);
		}
		
		// Generate exponential random number
		private double getExponential()
		{
			return Xmin - (EDExponent * Math.Log(1.0 - MyRandom.NextDouble()));
		}

		// Generate truncated exponential variates
		//	From	Matt Shotwell
		//			Graduate Student
		//			Div. Biostatistics and Epidemiology
		//			Medical University of South Carolina  
		//	itexp <- function(u, m, t) { -log(1-u*(1-exp(-t*m)))/m }
		//
		//	The above function does not include the xmin parameter
		//	With xmin I think it becomes (in r)
		//
		//	itexp <- function(U, lambda, Xmin, Xmax) {Xmin -log(1-U*(1-exp(-(Xmax-Xmin)*lambda)))/lambda }
		//
		private double getTruncatedExponential()
		{
			//	using x = {Xmin-log(1-R*(1-exp(-(Xmax-Xmin)*lambda)))/lambda }
			return Xmin - Math.Log(MyRandom.NextDouble() * (1.0 - Math.Exp(-(Xmax - Xmin) * Exponent))) / Exponent;
		}
			
		// Generate Truncated Pareto random number
		//	See YY Kagan 2002 eq 41-43
		//  step = Mt {R[1-(Mxp/Mt)^-b]+(Mxp/Mt)^-b}^-1/b
		//	Mt = Xmin; Mxp = Xmax; 
		private double getTruncatedPareto()
		{
			return Xmin * Math.Pow(MyRandom.NextDouble() * TPTerm1 + TPTerm2, TPTerm3);
		}

        // RNGs for the Gamma, Normal and LogNormals distributions
        //  These would be better in their own class I think, or as part of MLE_Random perhaps
        private double LogNormalNextDouble()
        {
            return Math.Exp(NormalNextDouble() * Sigma + Mu);
        }

        private double NormalNextDouble()
        {
            double mu = 0.0, sigma = 1.0;

            if (ND_Return_Next)
            {
                ND_Return_Next = false;
                return ND_NextVariate;
            }
            else
            {
                ND_Return_Next = true;

                while (true)
                {
                    double v1 = 2.0 * MyRandom.NextDouble() - 1.0;
                    double v2 = 2.0 * MyRandom.NextDouble() - 1.0;
                    double rsq = v1 * v1 + v2 * v2;

                    if (rsq <= 1)
                    {
                        double y = Math.Sqrt(-2.0 * Math.Log(rsq) / rsq) * sigma;
                        ND_NextVariate = v2 * y + mu;
                        return v1 * y + mu;
                    }
                }
            }
        }

        private double GammaNextDouble()
        {
            double xi, x, gen1, gen2;
            do
            {
                gen1 = 1.0 - MyRandom.NextDouble();
                gen2 = 1.0 - MyRandom.NextDouble();

                if (gen1 <= GH2)
                {
                    xi = Math.Pow(gen1 / GH2, 1.0 / GH1);
                    x = gen2 * Math.Pow(xi, GH1 - 1.0);
                }
                else
                {
                    xi = 1.0 - Math.Log((gen1 - GH2) / (1.0 - GH2));
                    x = gen2 * Math.Pow(Math.E, -xi);
                }
            } while (x > Math.Pow(xi, GH1 - 1.0) * Math.Pow(Math.E, -xi));

            for (int i = 1; i <= Alpha; i++)
            {
                xi -= Math.Log(MyRandom.NextDouble());
            }

            return xi * Theta;
        }
    }
}
