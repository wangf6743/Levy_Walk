using System.Collections.Generic;
using System;

namespace MBA_MLE_Analysis
{
	public class Track
	{
		// Class variables
		public static bool		XY_Data, Z_Data, LatLon_Data, Depth_Data, Step_Data;
		public static TimeSpan	MinGap, MaxGap;
		public static double	MinStep, MaxStep;
		public static string	Filename;

		// Member variables
		public TStep[]	TSteps;
		public int		IgnoredTrackGaps, CoalesedSteps, ZeroSteps;

		// Global work variables for step array creation
		private double step, LastStep, AbsStep, Xmin, Xmax;
		private List<double> FilteredSteps;

		// Simple constructor
		public Track(string p_Filename)
		{
			Filename = p_Filename;
			IgnoredTrackGaps = 0;
			CoalesedSteps = 0;
			XY_Data = false;
			Z_Data = false;
			LatLon_Data = false;
			Depth_Data = false;
			Step_Data = false;
			MaxGap = new TimeSpan();
			MinGap = TimeSpan.MaxValue;
			MaxStep = 0;
			MinStep = double.PositiveInfinity;

			// Reset the step calculation stuff in TStep
			TStep.Reset();
		}

		// Add the list of points built during import
		public void AddPoints(List<TStep> p_TSteps)
		{
			TSteps = p_TSteps.ToArray();
		}

		// General accessor methods
		public	int		getNoOfPoints()		{ return TSteps.Length; }	// Note that steps must be 1 less than the number of imported points
		public	string	getMaxGap()			{ return MaxGap.ToString(); }

		public	static string	getShortFileName()	{ return Filename.Substring(Filename.LastIndexOf("\\") + 1);}
		
		// Get steps in X, Y or Z
		public double[] getSteps()
		{
			// Initialise the Xmin and Xmax parameters
			if (Parameters.MLE_Xmin > 0)	Xmin = Parameters.MLE_Xmin;
			else							Xmin = 0.0000000001F;

			if (Parameters.MLE_Xmax > 0)	Xmax = Parameters.MLE_Xmax;
			else							Xmax = double.MaxValue;

			// Initialise other variables
			FilteredSteps = new List<double>();
			step = 0;
			LastStep = 0;
			IgnoredTrackGaps = 0;
			CoalesedSteps = 0;

			// Process all the steps in TSteps
			foreach (TStep tp in TSteps)
			{
				if (Parameters.MLE_Dimension == 0)
				{
					if (Parameters.Coalese) getCoalesedSteps(tp.x, tp.Gap);
					else getSteps(tp.x, tp.Gap);
				}
				else if (Parameters.MLE_Dimension == 1)
				{
					if (Parameters.Coalese) getCoalesedSteps(tp.y, tp.Gap);
					else getSteps(tp.y, tp.Gap);
				}
				else
				{
					if (Parameters.Coalese) getCoalesedSteps(tp.z, tp.Gap);
					else getSteps(tp.z, tp.Gap);
				}
			}

			// Add the last step if > Xmin and < Xmax
			if (Parameters.Coalese && step >= Xmin && step <= Xmax)
			{
				FilteredSteps.Add(step);
			}

			ZeroSteps = TSteps.Length - CoalesedSteps - IgnoredTrackGaps - FilteredSteps.Count;
			return FilteredSteps.ToArray();
		}

		// Process coalesed steps
		private void getCoalesedSteps(double p_Step, TimeSpan p_Gap)
		{
			AbsStep = Math.Abs(p_Step);

			// Ignore steps if the gap is too great
			if (Parameters.MaxGap.TotalSeconds > 0 && p_Gap.TotalSeconds > Parameters.MaxGap.TotalSeconds)
			{
				IgnoredTrackGaps++;

				// Ignore steps < Xmin or > Xmax
				if (step >= Xmin && step <= Xmax)
				{
					FilteredSteps.Add(step);
				}

				LastStep = 0;
				step = 0;
				return;
			}

			// If there has been no change in direction accumulate the step
			if (Math.Sign(p_Step) == Math.Sign(LastStep))
			{
				step += AbsStep;
				CoalesedSteps++;
			}
			else
			{
				// Ignore steps < Xmin or > Xmax
				if (step >= Xmin && step <= Xmax)
				{
					FilteredSteps.Add(step);
				}

				step = AbsStep;
			}

			LastStep = p_Step;
		}

		// Process all steps
		private void getSteps(double p_Step, TimeSpan p_Gap)
		{
			AbsStep = Math.Abs(p_Step);

			// Ignore steps if the gap is too great
			if (Parameters.MaxGap.TotalSeconds > 0 && p_Gap.TotalSeconds > Parameters.MaxGap.TotalSeconds)
			{
				IgnoredTrackGaps++;
			}
			else
			{
				// Ignore steps < Xmin or > Xmax
				if (AbsStep >= Xmin && AbsStep <= Xmax)
				{
					FilteredSteps.Add(AbsStep);
				}
			}
		}
	}
}
