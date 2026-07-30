	// Collect together all the GOF tests
using System;

namespace MBA_MLE_Analysis
{
	public class GOF
	{
		// Kolmogorov-Smirnov test
		public static double Kolmogorov_Smirnov(double[] s1, double[] s2)
		{
			return Kolmogorov_Smirnov(s1, s2, true, true);
		}
	
		public static double Kolmogorov_Smirnov(double[] s1, double[] s2, bool p_SortS1, bool p_SortS2)
		{
			double		p1, p2;		
			double		D = 0, NewD = 0;					// D values for the K-S test
			double[]	ranked;								// Array of steps for the K-S test
			double		LastRankValue = -1.0;
			int			x, s1x = 0, s2x = 0;
			double		s1len, s2len;
			
			// Store array lengths for p-value calculations
			s1len = s1.Length;
			s2len = s2.Length;
			
			// Sort the two sample arrays s1 & s2 
			if (p_SortS1) Array.Sort(s1);
			if (p_SortS2) Array.Sort(s2);
	
			// Create the array to hold ranked values
			ranked = new double[s1.Length + s2.Length];
			
			// Add all values to the ranked array, and sort them while doing so
			for (x = 0; x < ranked.Length; x++)
			{
				// Is there a choice?
				if (s1x < s1len && s2x < s2len)
				{
					if (s1[s1x] < s2[s2x]) ranked[x] = s1[s1x++];
					else				   ranked[x] = s2[s2x++];
				}
				
				// If not then fill up from which ever sample array still has elements
				else
				{
					if (s1x < s1len) ranked[x] = s1[s1x++];
					else		 	 ranked[x] = s2[s2x++];
				}
			}
			
			// Reset indices
			s1x = 0;
			s2x = 0;
			
			// Calculate the D value for the K-S test
			//	Calculate the proportion of values in each set of samples that are <= each value in the ranked array 
			for (x = 0; x < ranked.Length; x++)
			{
				if (ranked[x] > LastRankValue)
				{
					LastRankValue = ranked[x];
	
					while (s1x < s1len && s1[s1x] <= LastRankValue) s1x++;
					while (s2x < s2len && s2[s2x] <= LastRankValue) s2x++;
				
					p1 = (double)s1x / s1len;
					p2 = (double)s2x / s2len;
					NewD = Math.Abs(p1 - p2);
				
					if (NewD > D) D = NewD;
				}
			}
			
			return D;
		}
	}
}
