// A class to store time values, as opposed to DateTime values
//	where times are held simply as hours, minutes and seconds
//	to allow simpler use of time values in situations such as track gap checking
//	where 29:30:00 might be required
using System;
using System.Text;

namespace MBA_MLE_Analysis
{
	public class Time
	{
		private static char[] split = { ':' };

		private int hhh, mm, ss, seconds;

		// Full constructor
		public Time(int Hours, int Minutes, int Seconds)
		{
			hhh = Hours;
			mm = Minutes;
			ss = Seconds;

			// Seconds cannot be > 60
			if (ss > 59)
			{
				mm += (ss / 60);
				ss = ss % 60;
			}

			// Minutes cannot be > 60
			if (mm > 59)
			{
				hhh += (mm / 60);
				mm = mm % 60;
			}

			SetSeconds();
		}

		private void SetSeconds()
		{
			seconds = (hhh * 3600) + (mm * 60) + ss;
		}

		// Constructor with just seconds
		public Time(int Seconds)
		{
			FromSeconds(Seconds);
		}

		private void FromSeconds(int Seconds)
		{
			seconds = Seconds;

			if (Seconds > 3599)
			{
				hhh = Seconds / 3600;
				Seconds = Seconds % 3600;
			}

			if (Seconds > 59)
			{
				mm = Seconds / 60;
				Seconds = Seconds % 60;
			}

			ss = Seconds;
		}

		// Derive time from a string (e.g. 123:27:22)
		public Time(string p_Time)
		{
			string[] parsed;
			double h = 0, m = 0, s = 0;		// To allow the convienience of decimal hours etc

			//	First lets see how many colons there are
			parsed = p_Time.Trim().Split(split, StringSplitOptions.RemoveEmptyEntries);

			// The logic will be - no colons means we just have seconds
			//	one colon means minutes & seconds
			//	two colons is hours, mins and seconds
			if (parsed.Length == 1) s = Convert.ToDouble(parsed[0]);
			else if (parsed.Length == 2)
			{
				m = Convert.ToDouble(parsed[0]);
				s = Convert.ToDouble(parsed[1]);
			}
			else if (parsed.Length == 3)
			{
				h = Convert.ToDouble(parsed[0]);
				m = Convert.ToDouble(parsed[1]);
				s = Convert.ToDouble(parsed[2]);
			}

			// Convert from doubles to ints
			FromSeconds((int)((h * 3600) + (m * 60) + s));
		}

		// Return a seconds value
		public int getSeconds()
		{
			return seconds;
		}

		// Return an edited string
		public override string ToString()
		{
			string s;

			// Make sure the hours are formatted correctly
			if (hhh > 99)	s = hhh.ToString();
			else			s = hhh.ToString("D2");

			return s + ":" + mm.ToString("D2") + ":" + ss.ToString("D2");
		}

		// Equality
		public bool Equals(int p_Seconds)
		{
			return p_Seconds == seconds;
		}

		// Quick check for zero
		public bool Zero()
		{
			return seconds == 0;
		}
	}
}
