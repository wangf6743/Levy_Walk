// Create & return a track from a CSV file in a format that is defined by the first line
//	The header is used to specify the contents of the columns using the following tags:
//	
//	Date, X, Y, LAT, LON, Depth

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{
	public class Imp_CSV
	{
        private static readonly DateTimeFormatInfo DTFI_Current = CultureInfo.CurrentCulture.DateTimeFormat;
        private static readonly DateTimeFormatInfo DTFI_GB = CultureInfo.GetCultureInfo("en-GB").DateTimeFormat;
        private static DateTimeFormatInfo DTFI;
        private static	StreamReader	MyReader;		// The input file reader 
		private static	int				i_Date, i_x, i_y, i_z, i_Depth, i_Lat, i_Lon, i_Altitude, i_Steps;
		private static  string			input;
		private static  string[]		parsed;
		private static  List<TStep>		TSteps;
        private static readonly char[]          Separator = { ',' };

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
	        double		x = 0, y = 0, z = 0, depth = 0, latitude = 0, longitude = 0, altitude = 0, step = 0;
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
			if (i_x > -1 && i_y > -1)
			{
				i_Lat = i_Lon = i_Depth = i_Steps = -1;
				Track.XYData = true;

				// Record whether Z was also provided
				if (i_z > -1) Track.ZData = true;
			}

			// If Lat and long are set then we use them
			else if (i_Lat > -1 && i_Lon > -1)
			{
				i_x = i_y = i_z = i_Depth = i_Steps = -1;
				Track.LatLonData = true;

                // Record whether Altitude was also provided
                if (i_Altitude > -1) Track.AltData = true;
            }

            // Use depth if we have it
            else if (i_Depth > -1)
			{
				i_x = i_y = i_z = i_Lat = i_Lon = i_Steps = -1;
				Track.DepthData = true;
			}

			// Use steps if we have it
			else if (i_Steps > -1)
			{
				i_x = i_y = i_z = i_Lat = i_Lon = i_Depth = -1;
				Track.StepData = true;
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
                if (input == null || input.Replace(',', ' ').Trim().Length == 0 || input.Replace(';', ' ').Trim().Length == 0) return true;
	            
	            // Otherwise parse the data
	            parsed = input.Split(Separator);
	        
				// Extract the fields
				try {
					// If a date is provided then extract it using the current culture, otherwise just add 10 seconds
                    if (i_Date > -1) time = Convert.ToDateTime(parsed[i_Date], DTFI);
					else			time = time.AddSeconds(10);
				
					// Extract x
                    if (i_x > -1) x = Convert.ToDouble(parsed[i_x], DTFI);
				
					// Extract y
                    if (i_y > -1) y = Convert.ToDouble(parsed[i_y], DTFI);

					// Extract z
                    if (i_z > -1) z = Convert.ToDouble(parsed[i_z], DTFI);

					// Extract depth
                    if (i_Depth > -1) depth = Convert.ToDouble(parsed[i_Depth], DTFI);

                    // Extract altitude
                    if (i_Altitude > -1) altitude = Convert.ToDouble(parsed[i_Altitude], DTFI);

                    // Extract latitude
                    if (i_Lat > -1) latitude = Convert.ToDouble(parsed[i_Lat], DTFI);
	        
					// Extract latitude 
                    if (i_Lon > -1) longitude = Convert.ToDouble(parsed[i_Lon], DTFI);

					// Extract a step length 
                    if (i_Steps > -1) step = Convert.ToDouble(parsed[i_Steps], DTFI);
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
				if (i_Lat > -1)			TSteps.Add(new TStep(time, latitude, longitude, altitude));
				else if (i_x > -1)		TSteps.Add(new TStep(time, x, y, z));
				else if (i_Depth > -1)	TSteps.Add(new TStep(time, depth));
				else if (i_Steps > -1)
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
			i_Date = i_x = i_y = i_z = i_Depth = i_Lat = i_Lon = i_Altitude = i_Steps = -1;

            // If the file is from Dive or Track analysis read until the header is found
            if (input.StartsWith("Track Analysis") || input.StartsWith("Dive Analysis"))
            {
                while (input != null && !input.StartsWith("ISO")) input = MyReader.ReadLine();

                if (input == null) return;
            }

            // Remove quotes
			input = input.Replace("\"", "");

            // Decide which column separator to use
            //  If we have multiple ; then use this, otherwise ,
            if (input.Contains(";"))
            {
                DTFI = DTFI_Current;
                Separator[0] = ';';
            }
            else
            {
                DTFI = DTFI_GB;
                Separator[0] = ',';
            }

			// Parse the first line to determine how many columns there are and what the content is
			parsed = input.Split(Separator);

			// Check each non-null entry and set the column content pointers
			for (int i = 0; i < parsed.Length; i++)
			{
				if (parsed[i] == null) { }

                else if (parsed[i].Equals("ISO Time", StringComparison.OrdinalIgnoreCase)) i_Date = i;
				else if (parsed[i].Equals("ISO Date", StringComparison.OrdinalIgnoreCase)) i_Date = i;
				else if (parsed[i].Equals("Date", StringComparison.OrdinalIgnoreCase)) i_Date = i;
				else if (parsed[i].Equals("X", StringComparison.OrdinalIgnoreCase)) i_x = i;
				else if (parsed[i].Equals("Y", StringComparison.OrdinalIgnoreCase)) i_y = i;
				else if (parsed[i].Equals("Z", StringComparison.OrdinalIgnoreCase)) i_z = i;
				else if (parsed[i].Equals("Depth", StringComparison.OrdinalIgnoreCase)) i_Depth = i;
				else if (parsed[i].Equals("LAT", StringComparison.OrdinalIgnoreCase)) i_Lat = i;
				else if (parsed[i].Equals("LON", StringComparison.OrdinalIgnoreCase)) i_Lon = i;
				else if (parsed[i].Equals("LONG", StringComparison.OrdinalIgnoreCase)) i_Lon = i;
				else if (parsed[i].Equals("LATITUDE", StringComparison.OrdinalIgnoreCase)) i_Lat = i;
				else if (parsed[i].Equals("LONGITUDE", StringComparison.OrdinalIgnoreCase)) i_Lon = i;
                else if (parsed[i].Equals("Altitude", StringComparison.OrdinalIgnoreCase)) i_Altitude = i;
                else if (parsed[i].Equals("STEPS", StringComparison.OrdinalIgnoreCase)) i_Steps = i;
			}

			// If we have X, Y and Depth, treat depth as Z
			if (i_x > -1 && i_y > -1 && i_Depth > -1)
			{
				i_z = i_Depth;
				i_Depth = -1;
			}
		}
	}
}
