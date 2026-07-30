	// This class contains the code to perform latitude-longitude to ECEF to Local Tangent Plane conversions
	//	i.e. Lat Long to X Y
	//	
using System;

namespace MBA_MLE_Analysis
{
	public class ECEF
	{
		private const double	a = 6378137.0F,				// WSG84 Semimajor axis
								e = 0.08181919084262F,		// Eccentricity
								esq = e * e,				// e squared
								c_DegreesToRadians = (double) (Math.PI / 180.0);
		
		private	static double	x, y;
			
		// Convert from LAT LONG to Plate Carree
		//	This method : the lat long to Plate Carree conversion as described in Coordinate Conversions and Transformations including Formulas.pdf
		//	in the track analysis folder
		public static void LatLongToPlateCarree(double p_latitude, double p_longitude)
		{
			double	latitude,
					longitude;
			
			// Extract latitude & longitude and convert to radians
			latitude = DegreesToRadians(p_latitude);
			longitude = DegreesToRadians(p_longitude);
					
			// The Plate Carree coordinates can be calculated from the geodetic as
			//	E = FE + R (Long � Long0) cos(Lat0) 
			//	N = FN + R Lat
			
			//	As FE, FN, Lat0 and Long0 are all zero 
			//	and E=X, N=Y, and R=a this becomes
			
			//	X = a * Long
			//	Y = a * Lat
			x = a * longitude;
			y = a * latitude;	
		}

		// Convert degrees to radians
		public static double DegreesToRadians(double d)		{return c_DegreesToRadians * d;}
		public static double RadiansToDegrees(double d)		{return d / c_DegreesToRadians;}
		
		// Return converted coordinates
		public static double getX()	{return x;}
		public static double getY()	{return y;}
	}
}
