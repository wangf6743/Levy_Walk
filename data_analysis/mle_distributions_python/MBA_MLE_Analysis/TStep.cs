// This class holds data for a single imported point
// The data points will store steps and gaps which will be computed on import t save time
using System;

namespace MBA_MLE_Analysis
{
	public class TStep
	{
		private static double	LastX, LastY, LastZ;
		private static DateTime LastDate;
		private static bool		FirstPoint;
		
		// Hold steps and gaps
		public double	x, y, z;
		public TimeSpan	Gap;

		// Reset the last values to start a new import
		public static void Reset()
		{
			FirstPoint = true;
		}

		// Import a point and calculate the steps and gaps
		//	This constructor works for both XY and LatLong data
		//	The first imported point neccessarily is a zero step
		public TStep (DateTime p_Date, double p_x, double p_y, double p_z)
		{
			if (Track.LatLon_Data)	setLatLon(p_x, p_y);
			else					setXYZ(p_x, p_y, p_z);

			if (!FirstPoint) Gap = p_Date.Subtract(LastDate);
			else			 Gap = new TimeSpan();

			if (!FirstPoint)
			{
				setMinMaxGap();
				setMinMaxStep(Math.Abs(x));
				setMinMaxStep(Math.Abs(y));
				setMinMaxStep(Math.Abs(z));
			}

			LastDate = p_Date;
			FirstPoint = false;
		}

		private void setMinMaxStep(double p)
		{
			if (p > Track.MaxStep) Track.MaxStep = p;
			if (p < Track.MinStep) Track.MinStep = p;
		}

		private void setMinMaxGap()
		{
			if (Gap.CompareTo(Track.MaxGap) > 0) Track.MaxGap = Gap;
			if (Gap.CompareTo(Track.MinGap) < 0) Track.MinGap = Gap;
		}

		private void setLatLon(double p_x, double p_y)
		{
			ECEF.LatLongToPlateCarree(p_x, p_y);

			if (!FirstPoint)
			{
				x = LastX - ECEF.getX();
				y = LastY - ECEF.getY();
			}

			LastX = ECEF.getX();
			LastY = ECEF.getY();
		}

		private void setXYZ(double p_x, double p_y, double p_z)
		{
			if (!FirstPoint)
			{
				x = LastX - p_x;
				y = LastY - p_y;
				z = LastZ - p_z;
			}

			LastX = p_x;
			LastY = p_y;
			LastZ = p_z;
		}
	
		// Import just a depth, it will be held in the X dimension
		public TStep (DateTime p_Date, double p_depth)
		{
			if (!FirstPoint)
			{
				Gap = p_Date.Subtract(LastDate);
				x = LastX - p_depth;
			}

			LastDate = p_Date;
			LastX = p_depth;
			setMinMaxGap();
			setMinMaxStep(Math.Abs(x));
			FirstPoint = false;
		}

		// Import a step length
		public TStep(double p_Step)
		{
			x = p_Step;
			Gap = new TimeSpan(0, 0, 1);
			setMinMaxGap();
			setMinMaxStep(Math.Abs(x));
		}
	}
}
