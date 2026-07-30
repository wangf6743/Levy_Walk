// This static class is a helper class for the MLE stuff
//	and has methods for MLEs, log-likelihoods as well as Random and Good test data creation

//	All the methods here expect the steps array to have been trimmed to contain no values < Xmin or > Xmax
//		all the existing methods that use these methods do trim the array

using System;

namespace MBA_MLE_Analysis
{
    public class MLEX
    {
        public static string[] Distribution = { "Power", "Exponential", "Truncated Pareto", "Truncated Exponential", "Gamma", "Log Normal" };

        
        // Magic numbers for the Gamma function, needed for the MLE
        private static double[] GammaCof = { 76.18009172947146,-86.50532032941677,
												24.01409824083091,-1.231739572450155,
												0.1208650973866179e-2,-0.5395239384953e-5};

        //	Most of the data is a form of integer as data from DSTs will usually be in multiples of Xmin
        private static double Xmin;
        public static bool Discrete;
        
        //--------------------------------//
        //	MAXIMUM LIKELIHOOD ESTIMATORS //
        //--------------------------------//

        // Power law
        // Calculate a value of Alpha given an Xmin value using the steps array
        public static double Power_MLE(double[] steps, double Xmin)
        {
            // Calculate the sum of (log(step/Xmin))
            double sum = 0.0, n = (double)steps.Length;

            for (int x = 0; x < steps.Length; x++)
            {
                if (Discrete && Xmin > 0.5) sum += Math.Log(steps[x] / (Xmin - 0.5));
                else sum += Math.Log(steps[x] / Xmin);
            }

            // The equation in the paper is very confusing for me :(, we dont need to raise to power -1, just need to divide!
            if (sum > 0.0) return 1.0 + (n / sum);
            return 0.0;
        }

        // Exponential
        // Calculate a value of lambda given an Xmin value using the steps array
        public static double Exponential_MLE(double[] steps, double Xmin)
        {
            // Alpha can be estimated as n / SUM(x - Xmin) (Bradshaw & Sims - Solutions to problems associated with identifying Levy walk patterns
            double sum = 0.0, n = (double)steps.Length;

            for (int x = 0; x < steps.Length; x++)
            {
                sum += steps[x] - Xmin;
            }

            if (sum > 0.0) return n / sum;
            return 0;
        }

        // Truncated exponential distribution
        //	We will use the code from Julian Stander @ Plymouth and just seek to maximise the LLH
        //	This differs from the other methods here that use closed form solutions
        //	The TP method could work in the same way in fact
        public static double TruncatedExponential_MLE(double[] steps, double Xmin, double Xmax)
        {
            // We need to maximise the LLH 
            double LLH = 0.0, lambda, Bestlambda, LastLLH = Double.NegativeInfinity, BestLLH = Double.NegativeInfinity;
            double Q = 3.3, lambdaInc, stop = 0.0001;
            int Max = 200, Count = 0;

            // Start with an estimate of lambda
            lambda = Exponential_MLE(steps, Xmin);

            // Now search until we have maximised the LLH
            Bestlambda = lambda;
            lambdaInc = lambda / Q;
            lambda = lambda - lambdaInc;

            while (Math.Abs(lambdaInc) > stop && Count++ < Max)
            {
                // Increment (decrement) lambda for the next test
                lambda += lambdaInc;

                // Evaluate the estimator
                LLH = TE_LLH(steps, lambda, Xmin, Xmax);

                // If Lt is the best so far then store it
                if (LLH > BestLLH)
                {
                    Bestlambda = lambda;
                    BestLLH = LLH;
                }

                // If Lt is lower than the last value then work back the other way
                if (LLH < LastLLH)
                {
                    lambdaInc = -(lambdaInc / Q);
                }

                LastLLH = LLH;
            }

            return Bestlambda;
        }

        // Calculate a value for alpha for the Truncated Pareto distribution
        //	Method taken from White, E. P., B. J. Enquist, et al. (2008). "ON ESTIMATING THE EXPONENT OF POWER-LAW FREQUENCY DISTRIBUTIONS." Ecology 89(4): 905-912.
        //	Note that this numerical method starts with an estimate from calcPowerAlpha then adjusts the value to minimise y in 
        //	the equation y = -meanlogx-1/(lambda+1)+(xmax^(lambda+1)*log(xmax)-xmin^(lambda+1)*log(xmin))/(xmax^(lambda+1)-xmin^(lambda+1))

        //	The MATLAB code from which this is derived is :
        //		exponent = fzero(@(lambda) truncpareto_mle_equation(lambda,mean(log(data)),xmin,xmax),lambda0);
        //		
        //		    function [y] = truncpareto_mle_equation(lambda,meanlogx,xmin,xmax)
        //		    y=-meanlogx-1/(lambda+1)+(xmax^(lambda+1)*log(xmax)-xmin^(lambda+1)*log(xmin))/(xmax^(lambda+1)-xmin^(lambda+1));
        //	Yuk, but hey, it works ;-)
        public static double TrucatedPareto_MLE(double[] steps, double Xmin, double Xmax)
        {
            double lambda, BestLambda, LastY = Double.MaxValue, BestY = Double.MaxValue;
            double Q = 3.3, lambdaInc, stop = 0.001;
            double meanlogx, sum = 0.0, sumlogx = 0.0;
            double n = 0.0, y = 1.0;
            double logXmax, logXmin, LambdaPlus1;
            int Max = 100, Count = 0;

            // Calculate mean(log(data))
            //	NOTE: The steps array will have been trimmed at this point, so no values will be < Xmin or > Xmax
            for (int x = 0; x < steps.Length; x++)
            {
                sum += Math.Log(steps[x]);
                sumlogx += Math.Log(steps[x]) - Math.Log(Xmin);
                n++;
            }

            meanlogx = sum / n;

            // Calculate Math.Log(Xmax) & Math.Log(Xmin)
            logXmax = Math.Log(Xmax);
            logXmin = Math.Log(Xmin);

            // Start with an estimate from calcParetoAlpha
            lambda = -Power_MLE(steps, Xmin);

            // Now search until a close to zero result is obtained
            BestLambda = lambda;
            lambdaInc = lambda / Q;
            lambda = lambda - lambdaInc;

            while (y != 0.0 && Math.Abs(lambdaInc) > stop && Count++ < Max)
            {
                // Increment (decrement) lambda for the next test
                lambda += lambdaInc;
                LambdaPlus1 = lambda + 1.0;

                // Calculate the result of the equation
                //	y=-meanlogx-1/(lambda+1)+(xmax^(lambda+1)*log(xmax)-xmin^(lambda+1)*log(xmin))/(xmax^(lambda+1)-xmin^(lambda+1));
                y = -meanlogx - 1.0 / LambdaPlus1 + (Math.Pow(Xmax, LambdaPlus1) * logXmax - Math.Pow(Xmin, LambdaPlus1) * logXmin) / (Math.Pow(Xmax, LambdaPlus1) - Math.Pow(Xmin, LambdaPlus1));
                y = Math.Abs(y);

                if (y < BestY)	// NOTE: The first value is always stored as BestY starts as Double.MaxValue
                {
                    BestLambda = lambda;
                    BestY = y;
                }

                if (y > Math.Abs(LastY))	// NOTE: The first value is always ignored as Lasty starts as MaxValue
                {
                    lambdaInc = -(lambdaInc / Q);
                }

                LastY = y;
            }

            return -BestLambda;
        }

        // Gamma distribution
        //  All the blurb for this is on the Wiki page
        //  The MLE returns two parameters, the shape and scale
        //  We have an approximation for the shape which is within 1.5%, so I think that is close enough
        //  Given that we can then compute the scale.
        //  The parameters are returned in a PointD
        public static PointD Gamma_MLE(double[] steps)
        {
            double Meanlnxn = 0,
                    lnMeanx,
                    sumx = 0,
                    s, shape, scale, N;

            N = (double)steps.Length;

            // Calculate the variable s where S = Math.Log(Mean(x)) – Mean(Math.log(x))
            foreach (double x in steps)
            {
                sumx += x;
                Meanlnxn += Math.Log(x);
            }

            lnMeanx = Math.Log(sumx / N);
            Meanlnxn = Meanlnxn / N;
            s = lnMeanx - Meanlnxn;

            // Now we can estimate K (shape)
            //  K = [3 – s + sqrt((s-3)^2 + 24s)] / 12s
            shape = (3.0 - s + Math.Sqrt(Math.Pow(s - 3, 2.0) + 24 * s)) / (12 * s);

            // Now we can estimate scale
            //  scale = (1/(shape*N)) * sumx
            scale = (1.0 / (shape * N)) * sumx;

            // Return them in the PointD
            return new PointD(shape, scale);
        }

        // Log normal
        //	Here we have two parameters and this doesn't really fit with the structure of the other distribuions
        //	We have no xmin / xmax parameters
        //	We have the mean & S.D, designated as mu and sd.
        //	To collect both we can return a PointD with X=mu and Y = sd
        //	mu = sum(ln x) / n; sd = sum(ln x - mu)^2 / n
        public static PointD LogNormal_MLE(double[] steps)
        {
            double sum = 0,
                   N = (double)steps.Length;

            PointD ln = new PointD();

            // Calculate the mean (mu)
            foreach (double x in steps) sum += Math.Log(x);

            ln.X = sum / N;

            // Calculate SD, for which we need the mean
            sum = 0;
            foreach (double x in steps) sum += Math.Pow(Math.Log(x) - ln.X, 2.0);

            ln.Y = Math.Sqrt(sum / N);

            return ln;
        }




        //--------------------------//
        // LOG-LIKELIHOOD Functions //
        //--------------------------//

        // Power law
        //	LLH = (n ln(mu - 1.0)) - (n ln Xmin) - (mu * SUM(ln (x/xmin)))
        //	From Power laws, Pareto distributions and Zipf's law	MEJ Newman, Comntemporary Physics 46, 323-351 eq B4
        //	Also in Bradshaw & Sims - Solutions to problems associated with identifying Levy walk patterns
        public static double Power_LLH(double[] steps, double Alpha, double Xmin)
        {
            double sum = 0.0, n = (double)steps.Length, term1, term2, term3;	// These are the three terms (parts) of the big sum above

            for (int x = 0; x < steps.Length; x++) sum += Math.Log(steps[x] / Xmin);

            term1 = n * Math.Log(Alpha - 1.0);
            term2 = n * Math.Log(Xmin);
            term3 = Alpha * sum;

            return term1 - term2 - term3;
        }


        // Exponential
        //	LLH = n (ln(lambda) + lambda * Xmin) - (lambda * SUM(x))
        //	Aaron Clauset, personal communication
        public static double Exponential_LLH(double[] steps, double Alpha, double Xmin)
        {
            double sum = 0.0, n = (double)steps.Length;

            foreach (double d in steps) sum += d;

            return n * (Math.Log(Alpha) + Alpha * Xmin) - (Alpha * sum);
        }

        // Truncated Pareto
        //	Using equation 39 from Edwards 2011. This handles values of mu < 1

        //				(		  mu - 1        )	
        //	llh  =	n ln(-----------------------)	- mu Sum(ln x)
        //				( Xmin^1-mu - Xmax^1-mu )

        //	Note that here a is Xmin, b is Xmax
        public static double TP_LLH(double[] steps, double mu, double Xmin, double Xmax)
        {
            double sum = 0.0, n = (double)steps.Length, term1, term2, term3, llh;

            // Calculate mu Sum (ln x)
            foreach (double d in steps) sum += Math.Log(d);

            // Perform the calculations
            term1 = (Math.Pow(Xmin, 1.0 - mu) - Math.Pow(Xmax, 1.0 - mu));

            // Very rarely term1 will be zero
            if (term1 == 0.0) return 0.0;

            // Complete the calculation
            term2 = n * Math.Log((mu - 1.0) / term1);
            term3 = mu * sum;
            llh = term2 - term3;

            return llh;
        }

        // Truncated exponential
        //	From Julian Stander, Plymouth [J.Stander@plymouth.ac.uk]
        //	r code...
        //	LLH = n*log(lambda) - lambda*sum(x) - n*log( exp(-lambda*a) - exp(-lambda*b) )
        //		Where a = Xmin; b = Xmax; x is the dataset
        public static double TE_LLH(double[] steps, double lambda, double Xmin, double Xmax)
        {
            double sum = 0.0, n = (double)steps.Length, term1, term2, term3, llh;

            // Calculate mu Sum (ln x)
            foreach (double d in steps) sum += d;

            //	Term1 [n*log(lambda)]
            term1 = n * Math.Log(lambda);

            //	Term2 [lambda*sum(xt)]
            term2 = lambda * sum;

            //	Term3 [n*log( exp(-lambda*a) - exp(-lambda*b) )]
            term3 = n * Math.Log(Math.Exp(-lambda * Xmin) - Math.Exp(-lambda * Xmax));

            llh = term1 - term2 - term3;
            return llh;
        }

        // Gamma
        //	Here we have two parameters and this doesn't really fit with the structure of the other distribuions
        //	We have no xmin / xmax parameters
        //	We have shape & scale and we need a Gamma (or rather ln gamma) function
        //		llh = (shape – 1) sum(ln x) – sum(x/scale) – (N*shape* ln(scale)) – (N * lnGamma(shape))
        public static double Gamma_LLH(double[] steps, double shape, double scale)
        {
            double sumLnx = 0,
                    sumxoverscale = 0,
                    N;

            N = (double)steps.Length;

            foreach (double x in steps)
            {
                sumLnx += Math.Log(x);
                sumxoverscale += (x / scale);
            }

            return (shape - 1) * sumLnx - sumxoverscale - (N * shape * Math.Log(scale)) - (N * lnGamma(shape));
        }

        // Returns the value ln[Γ(xx)] for xx > 0.
        private static double lnGamma(double xx)
        {
            // Internal arithmetic will be done in double precision, a nicety that you can omit if five-figure
            // accuracy is good enough.

            double x, y, tmp, ser;
            int j;

            y = x = xx;
            tmp = x + 5.5;
            tmp -= (x + 0.5) * Math.Log(tmp);
            ser = 1.000000000190015;

            for (j = 0; j <= 5; j++) ser += GammaCof[j] / ++y;

            return -tmp + Math.Log(2.5066282746310005 * ser / x);
        }

        // Log Normal
        //	Here we have two parameters and this doesn't really fit with the structure of the other distribuions
        //	We have no xmin / xmax parameters
        //	We have mean & s.d. 
        //		llh = = -sum(log(x))– Nlog(sd*math.sqrt(2*pi))- [(1/2*sd^2)*sum(log(x)-mean)^2
        public static double LogNormal_LLH(double[] steps, double mean, double sd)
        {
            double sumLnx = 0,
                    sumlnxminusmean = 0,
                    term2,
                    term3,
                    N;

            N = (double)steps.Length;

            // Calculate sum(ln(x)
            foreach (double x in steps)
            {
                sumLnx += Math.Log(x);
                sumlnxminusmean += Math.Pow(Math.Log(x) - mean, 2.0);
            }

            term2 = N * Math.Log(sd * Math.Sqrt(2.0 * Math.PI));
            term3 = (1.0 / (2.0 * Math.Pow(sd, 2.0))) * sumlnxminusmean;

            return -sumLnx - term2 - term3;
        }

        //---------------------------//
        // RANDOM TEST DATA CREATION //
        //---------------------------//

        // Power law
        public static void getPowerData(double[] testD, double Alpha, double Xmin)
        {
            MLE_Random MyRandom = new MLE_Random(MLE_Random.Power, Alpha, Xmin, 0);

            // Populate testD[] with random values from the proposed power law distribution using x = Xmin(1 - r)^-(1/(exponent-1))
            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = MyRandom.Next();

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Exponential
        public static void getExponentialData(double[] testD, double Alpha, double Xmin)
        {
            MLE_Random MyRandom = new MLE_Random(MLE_Random.Exponential, Alpha, Xmin, 0);

            // Populate testD[] with random values from the proposed power law distribution using x = xmin - (1.0/alpha) * ln(1.0 - r)
            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = MyRandom.Next();

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Truncated exponential
        public static void getTruncatedExponentialData(double[] testD, double lambda, double Xmin, double Xmax)
        {
            MLE_Random MyRandom = new MLE_Random(MLE_Random.TruncatedExponential, lambda, Xmin, Xmax);

            // Populate testD[] with random values from the proposed truncated exponential distribution 
            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = MyRandom.Next();

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Truncated Pareto
        //	See YY Kagan 2002 (Geophys. J. Int. (2002) 148, 520�541) eq 40
        public static void getTruncatedParetoData(double[] testD, double Alpha, double Xmin, double Xmax)
        {
            MLE_Random MyRandom = new MLE_Random(MLE_Random.TruncatedPareto, Alpha, Xmin, Xmax);

            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = MyRandom.Next();

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Gamma
        public static void getGammaData(double[] testD, PointD p, double Xmin, double Xmax)
        {
            MLE_Random MyRandom = new MLE_Random(MLE_Random.Gamma, p);

            // Select the required number of variates
            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = MyRandom.Next();

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Log Normal
        public static void getLogNormalData(double[] testD, PointD p, double Xmin, double Xmax)
        {
            MLE_Random MyRandom = new MLE_Random(MLE_Random.LogNormal, p);

            // Select the required number of variates
            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = MyRandom.Next();

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        //-------------------------//
        // GOOD TEST DATA CREATION //
        //-------------------------//

        // These methods use the random number generator equations but with a "random number" in a sequential range from 0 to 1
        // Power law
        public static void getGoodPowerData(double[] testD, double Alpha, double Xmin)
        {
            double DAlpha = -1.0 / (Alpha - 1.0);
            double L = (double)testD.Length;

            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = Xmin * Math.Pow(1.0 - (x / L), DAlpha);

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Exponential
        public static void getGoodExponentialData(double[] testD, double Alpha, double Xmin)
        {
            double DAlpha = 1.0 / Alpha;
            double L = (double)testD.Length;

            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = Xmin - (DAlpha * Math.Log(1.0 - (x / L)));

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Truncated exponential
        public static void getGoodTruncatedExponentialData(double[] testD, double lambda, double Xmin, double Xmax)
        {
            double L = (double)testD.Length;
            double U;

            for (int x = 0; x < testD.Length; x++)
            {
                U = x / L;
                testD[x] = Xmin - Math.Log(1.0 - U * (1.0 - Math.Exp(-(Xmax - Xmin) * lambda))) / lambda;

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Generate Truncated Pareto test data
        public static void getGoodTruncatedParetoData(double[] testD, double Alpha, double Xmin, double Xmax)
        {
            double beta = Alpha - 1.0;
            double TPTerm1 = (1.0 - Math.Pow(Xmax / Xmin, -beta));
            double TPTerm2 = Math.Pow(Xmax / Xmin, -beta);
            double TPTerm3 = (-1.0 / beta);
            double L = testD.Length;

            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = Xmin * Math.Pow((1.0 - (x / L)) * TPTerm1 + TPTerm2, TPTerm3);

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        // Generate Gamma test data
        public static void getGoodGammaData(double[] testD, PointD p, double Xmin, double Xmax)
        {
			int inflate, x1 = 0;

			// We need to do something different here to generate the 'good' data
			//  we will generate a large number of variates, sort the array and then select every nth
			inflate = 50000000 / testD.Length;

            // Initialise the Gamma RNG
            MLE_Random MyRandom = new MLE_Random(MLE_Random.Gamma, p);

			// Use floats for the temporary random arrays to save memory
			float[] temp = new float[inflate * testD.Length];

			for (int x = 0; x < temp.Length; x++) temp[x] = (float)MyRandom.Next();

			// Now trim, sort and select
			Array.Sort(temp);

			// Rather than using Trim() just search for the start index
			while (temp[x1] < Xmin && x1 < temp.Length) x1++;

			// Adjust inflate to the new size 
			inflate = (int)((double)inflate * ((double)(temp.Length - x1) / (double)temp.Length));

			for (int x = 0; x < testD.Length; x++)
			{
				testD[x] = (double)temp[x1];
				x1 += inflate;

				if (Discrete) testD[x] = discrete(testD[x]);
			}
		}

        // Generate Log Normal test data
        public static void getGoodLogNormalData(double[] testD, PointD p, double Xmin, double Xmax)
        {
			int inflate, x1 = 0;

			// We need to do something different here to generate the 'good' data
			//  we will generate a large number of variates, sort the array and then select every nth
			inflate = 50000000 / testD.Length;

			// Initialise the log normal generator
            MLE_Random MyRandom = new MLE_Random(MLE_Random.LogNormal, p);

            // Use floats for the temporary random arrays to save memory
            float[] temp = new float[inflate * testD.Length];

            for (int x = 0; x < temp.Length; x++) temp[x] = (float)MyRandom.Next();

            // Now trim, sort and select
            Array.Sort(temp);

			// Rather than using Trim() just search for the start index
			while (temp[x1] < Xmin && x1 < temp.Length) x1++;

			// Adjust inflate to the new size 
			inflate = (int)((double)inflate * ((double)(temp.Length - x1) / (double)temp.Length));

            for (int x = 0; x < testD.Length; x++)
            {
                testD[x] = (double)temp[x1];
                x1 += inflate;

                if (Discrete) testD[x] = discrete(testD[x]);
            }
        }

        
        //-----------//
        // UTILITIES //
        //-----------//

        // Trim a sorted steps array so that it only contains values >= Xmin and <= Xmax
        public static double[] trim(double[] p_steps, double p_Min, double p_Max)
        {
            int j = 0,
                        Start = 0, End;
            double Max = Double.MaxValue, Min = 0;
            double[] s1;

            // Set min & max value
            if (p_Max > 0) Max = p_Max;
            if (p_Min > 0) Min = p_Min;
            if (Min >= Max) return p_steps;

            // Set (inclusive) start point (i.e. index where value >= Xmin)
            while (p_steps[Start] < Min) Start++;

            // Set start points for max search
            End = p_steps.Length - 1;

            // Set (inclusive) end point (i.e. index where value > Xmax)
            while (p_steps[End] > Max) End--;

            // Create the new array
            s1 = new double[1 + End - Start];

            // Rebuild the array to only have valid values
            for (int x = Start; x <= End; x++) s1[j++] = p_steps[x];

            return s1;
        }

        // Trim a sorted float steps array so that it only contains values >= Xmin and <= Xmax
        public static float[] trim(float[] p_steps, double p_Min, double p_Max)
        {
            int j = 0,
                        Start = 0, End;
            double Max = Double.MaxValue, Min = 0;
            float[] s1;

            // Set min & max value
            if (p_Max > 0) Max = p_Max;
            if (p_Min > 0) Min = p_Min;
            if (Min >= Max) return p_steps;

            // Set (inclusive) start point (i.e. index where value >= Xmin)
            while (p_steps[Start] < Min) Start++;

            // Set start points for max search
            End = p_steps.Length - 1;

            // Set (inclusive) end point (i.e. index where value > Xmax)
            while (p_steps[End] > Max) End--;

            // Create the new array
            s1 = new float[1 + End - Start];

            // Rebuild the array to only have valid values
            for (int x = Start; x <= End; x++) s1[j++] = p_steps[x];

            return s1;
        }


        // Convert a real step to a discrete step using the previously store value of Xmin
        public static double discrete(double step)
        {
            long div = (int)(step / Xmin);
            double sum = Xmin * div;
            double frac = step - sum;

            if (frac > (Xmin / 2.0)) sum += Xmin;

            return sum;
        }

        // Member variable access methods
        public static void setXmin(double p) { Xmin = p; }
        public static void setDiscrete(bool p) { Discrete = p; }
    }
}
