// Create & return a track from a CSV file in a format that is defined by the first line
//	The header is used to specify the contents of the columns using the following tags:
//	
//	Date, X, Y, LAT, LON, Depth

using System;
using System.Collections.Generic;
using System.IO;
using System.Windows.Forms;
using System.Globalization;

namespace MBA_MLE_Analysis
{
	public class ImpSmartCSV
	{
		// Member variables
		private static	DateTimeFormatInfo DTFI = CultureInfo.CurrentCulture.DateTimeFormat;

		private static	StreamReader	MyReader;		// The input file reader 
		private static	int				DATE, X, Y, Z, DEPTH, LAT, LON, STEPS;
		private static string			input;
		private static string[]			parsed;
		private static List<TStep>		TSteps;

		public static bool	OK;

	    // Import a track
	    public static bool Import(Track p_Track, Form1 p_Form)
	    {
			// Read the file and populate the Track list with points
	        OK = ReadFile(p_Track, p_Form);

			// If alls well add the points
			if (OK) p_Track.AddPoints(TSteps);

			if (MyReader != null) MyReader.Close();

			MyReader = null;
			TSteps = null;
			return OK;
	    }
	          
		// Populate the TSteps list
	    private static bool ReadFile(Track p_Track, Form1 p_Form)
		{   
	        double		x = 0, y = 0, z = 0, depth = 0, latitude = 0, longitude = 0, step = 0;
			DateTime	time = new DateTime();
			int			PointsRead = 0, Count = 0;
			bool		Positive = false;
			
			TSteps = new List<TStep>();

			// Create a buffered input stream to read the file and open it
			try
			{
				MyReader = new StreamReader(Track.Filename);

				// Read the first line, which should have headers
				input = MyReader.ReadLine();

				// Process the header line and determine column contents
				ReadHeader();
			}
			catch (Exception e)
			{
				MessageBox.Show("Error opening file\n" + e.Message, "File import error", MessageBoxButtons.OK, MessageBoxIcon.Error);
				return false;
			}
			
			// Validate the header data
			//	We can have either X&Y or LAT&LON or STEPS or DEPTH
			//	If we have X&Y then ignore anything else
			if (X > -1 && Y > -1)
			{
				LAT = LON = DEPTH = STEPS = -1;
				Track.XY_Data = true;

				// Record whether Z was also provided
				if (Z > -1) Track.Z_Data = true;
			}

			// If Lat and long are set then we use them
			else if (LAT > -1 && LON > -1)
			{
				X = Y = Z = DEPTH = STEPS = -1;
				Track.LatLon_Data = true;
			}

			// Use depth if we have it
			else if (DEPTH > -1)
			{
				X = Y = Z = LAT = LON = STEPS = -1;
				Track.Depth_Data = true;
			}

			// Use steps if we have it
			else if (STEPS > -1)
			{
				X = Y = Z = LAT = LON = DEPTH = -1;
				Track.Step_Data = true;
			}
			else
			{
				// We have missing data
				MessageBox.Show("Columns with X Y Z, Lat & Long, Depth or Steps must be provided",
								"File import error",
								MessageBoxButtons.OK, MessageBoxIcon.Error);
				return false;
			}	
	
			// Read data lines and parse according to the format defined in the header line
			while (true)
			{			
				input = MyReader.ReadLine();
	            
	            // If no line was read then EOF has been reached
	            if (input == null || input.Replace(',', ' ').Trim().Length == 0)  return true;
	            
	            // Otherwise parse the data
	            parsed = input.Split(',');
	        
				// Extract the fields
				try {
					// If a date is provided then extract it using the current culture, otherwise just add 10 seconds
					if (DATE > -1)  time = Convert.ToDateTime(parsed[DATE], DTFI);
					else			time = time.AddSeconds(10);
				
					// Extract x
					if (X > -1)	x = Convert.ToDouble(parsed[X]);
				
					// Extract y
					if (Y > -1)	y = Convert.ToDouble(parsed[Y]);

					// Extract z
					if (Z > -1) z = Convert.ToDouble(parsed[Z]);

					// Extract depth
					if (DEPTH > -1)	depth = Convert.ToDouble(parsed[DEPTH]);
				
					// Extract latitude
					if (LAT > -1) latitude = Convert.ToDouble(parsed[LAT]);
	        
					// Extract latitude 
					if (LON > -1) longitude = Convert.ToDouble(parsed[LON]);

					// Extract a step length 
					if (STEPS > -1) step = Convert.ToDouble(parsed[STEPS]);
				}
				catch (IndexOutOfRangeException)
				{
					MessageBox.Show("An error occured during the reading of the data in line:\n"
									+ input
									+ "\nData is missing from one or more columns.",
									"File import error", MessageBoxButtons.OK, MessageBoxIcon.Error);
					return false;
				}
				catch (Exception pe)
				{
					MessageBox.Show("An error occured during the reading of the data\n"
									+ pe.Message 
									+ "\nin line " + input 
									+ "\nCheck the format of the data and make sure that\nthe correct column headings have been used"
									+ "\nIt is preferable to use the ISO Date format (YYYY-MM-DD HH:MM:SS)",
									"File import error", MessageBoxButtons.OK, MessageBoxIcon.Error);
					return false;
				}
				
	            // Create the new point
				if (LAT > -1)			TSteps.Add(new TStep(time, latitude, longitude, z));
				else if (X > -1)		TSteps.Add(new TStep(time, x, y, z));
				else if (DEPTH > -1)	TSteps.Add(new TStep(time, depth));
				else if (STEPS > -1)
				{
					if (!Positive) step = -step;
					Positive = !Positive;
					TSteps.Add(new TStep(step));
				}
				
				PointsRead++;
				Count++;

				// Update the screen with a count of records read
				if (Count == 1000)
				{
					Count = 0;
					p_Form.l_Points.Text = PointsRead.ToString();
					Application.DoEvents();
				}
		    }
	    }

		private static void ReadHeader()
		{
			DATE = X = Y = Z = DEPTH = LAT = LON = STEPS = -1;

            // If the file is from Dive or Track analysis read until the header is found
            if (input.StartsWith("Track Analysis") || input.StartsWith("Dive Analysis"))
            {
                while (input != null && !input.StartsWith("ISO")) input = MyReader.ReadLine();

                if (input == null) return;
            }

            // Remove quotes
			input = input.Replace("\"", "");

			// Parse the first line to determine how many columns there are and what the content is
			parsed = input.Split(',');

			// Check each non-null entry and set the column content pointers
			for (int i = 0; i < parsed.Length; i++)
			{
				if (parsed[i] == null) { }

                else if (parsed[i].Equals("ISO Time", StringComparison.OrdinalIgnoreCase)) DATE = i;
                else if (parsed[i].Equals("Date", StringComparison.OrdinalIgnoreCase)) DATE = i;
				else if (parsed[i].Equals("X", StringComparison.OrdinalIgnoreCase)) X = i;
				else if (parsed[i].Equals("Y", StringComparison.OrdinalIgnoreCase)) Y = i;
				else if (parsed[i].Equals("Z", StringComparison.OrdinalIgnoreCase)) Z = i;
				else if (parsed[i].Equals("Depth", StringComparison.OrdinalIgnoreCase)) DEPTH = i;
				else if (parsed[i].Equals("LAT", StringComparison.OrdinalIgnoreCase)) LAT = i;
				else if (parsed[i].Equals("LON", StringComparison.OrdinalIgnoreCase)) LON = i;
				else if (parsed[i].Equals("LONG", StringComparison.OrdinalIgnoreCase)) LON = i;
				else if (parsed[i].Equals("LATITUDE", StringComparison.OrdinalIgnoreCase)) LAT = i;
				else if (parsed[i].Equals("LONGITUDE", StringComparison.OrdinalIgnoreCase)) LON = i;
				else if (parsed[i].Equals("STEPS", StringComparison.OrdinalIgnoreCase)) STEPS = i;
			}

			// If we have X, Y and Depth, treat depth as Z
			if (X > -1 && Y > -1 && DEPTH > -1)
			{
				Z = DEPTH;
				DEPTH = -1;
			}
		}
	}
}
