using System;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{
	class Parameters
	{
		public static TimeSpan	MaxGap;
		public static bool		Coalese;

		// MLE stuff
		public	static int		MLE_Fitting,			// 0=Normal; 1=No fitting; 2=Best fit Xmin
								MLE_WorseCount = 5,
								MLE_Dist = 0,			// The primary distribution to test
								MLE_Type = 0,			// Whether to analyse steps, waiting times, activity etc
								MLE_AltDist = 1,		// The alternate distribution for GOF, LLH & AICw
								MLE_Dimension = 0;		// 0=X, 1=Y, 2=Depth
		
		public static bool		MLE_Discrete, 
								MLE_p_Test;
		
		public static double	MLE_Xmin = 0,
								MLE_Xmax = 0;
	
		public static void		setMLE_Dist(ComboBox p)		
		{
			MLE_Dist = p.SelectedIndex;
			SetMLE_AltDist();
		}

		private static void SetMLE_AltDist()
		{
			// Set the default Alternate distribution
			if (MLE_Dist == 0) MLE_AltDist = 1;			// For P use E
			else if (MLE_Dist == 1) MLE_AltDist = 2;	// For E use TP
			else if (MLE_Dist == 2) MLE_AltDist = 1;	// For TP use E
			else if (MLE_Dist == 3) MLE_AltDist = 2;	// For TE use TP
		}
		
		public static void		setMLE_AltDist(ComboBox p)
		{
			MLE_AltDist = p.SelectedIndex;
			
			// If the distribution matches the primary distribution then reset it to the default
			if (MLE_AltDist == MLE_Dist)
			{
				SetMLE_AltDist();				
				p.SelectedIndex = MLE_AltDist;
			}	
		}

		public static void setMaxGap(TextBox tb)
		{
			Time t = new Time(tb.Text);
			MaxGap = new TimeSpan(0, 0, t.getSeconds());

			if (t.getSeconds() > 0) tb.Text = t.ToString();
			else tb.Text = "";
		}

		// Editing
		// Return a string representation of a number with either 2 or zero decimals, according to value
		public static string RoundD(double p)
		{
			if (p < 100) return p.ToString("F2");
			else return Math.Round(p, 0).ToString();
		}
	}
}
