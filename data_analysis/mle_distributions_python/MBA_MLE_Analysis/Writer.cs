//	This class provides a single output for CSV file data
//	and standardises the writing of heading lines
using System;
using System.IO;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{	
	public class Writer
	{
		public static string Version = "V1.0 2012-12-05";

		private	bool			OK = false;
		private StreamWriter	MyWriter;
		
		// This constructor prompts for the file name
		public Writer(Track p_Track, string p_Title, string p_FileID)
		{
			// Check the license
			//if (!MBA_Licence.MBA_Licence.OK) return;

			// Build the default name
			string FileName = get_FileName(Track.Filename, p_FileID);
			
			// If not Auto-Running then prompt to check the file name
			SaveFileDialog	SFD;

			SFD = new SaveFileDialog();
			SFD.Title = "Select a file for " + p_Title + " output";
			SFD.AddExtension = true;
			SFD.DefaultExt = ".csv";
			SFD.Filter = "CSV files|*.csv";
			SFD.ValidateNames = true;
			SFD.CheckPathExists = true;
			SFD.FileName = FileName;
		
			if (SFD.ShowDialog()!= DialogResult.OK) return;
		
			Application.DoEvents();
			FileName = SFD.FileName;
			
			// Open the file		
			OpenFile(FileName);
			
			if (OK) WriteSTDHeadings(p_Title, p_Track);
		}

		// Open the named file, checking that it opens OK and allowing a retry if it fails
		private void OpenFile(string FileName)
		{
			// Open the file ready for output
			while (!OK)
			{
				DialogResult reply = DialogResult.OK;
				
				try {MyWriter = new StreamWriter(FileName);} 
				catch (IOException)	
				{
					reply = MessageBox.Show("Error occured when opening file\n" + FileName + "\nMake sure the file is not open elsewhere." 
											,"Output file open error", MessageBoxButtons.RetryCancel, MessageBoxIcon.Exclamation);
					
					if (reply == DialogResult.Cancel) return;
				}
				
				if (reply == DialogResult.OK) OK = true;
			}
		}
		
		// Write the standard CSV file headings
		private void WriteSTDHeadings(string Title, Track p_Track)
		{
			WriteLine("MBA MLE Analysis - V1.0");
			WriteLine(Title + " (" + DateTime.Now.ToString() + " " + Environment.UserName + ")");
			
			WriteLine("File name," + Track.getShortFileName());
			WriteLine("Number of points," + p_Track.getNoOfPoints().ToString());
			WriteLine("");
		}

	
		// File name creation 
		//	Take the file name, find the end then replace the end with the code & .CSV
		public static string get_FileName(string p_FileName, string p_Code)
		{
			int x;
			string filename;
			
			// Find the end of the path and the start of the file name
			x = p_FileName.LastIndexOf("\\");
			filename = p_FileName.Substring(x);
			
			// Find the end of the file name (i.e. start of .csv)
			x = filename.LastIndexOf(".", StringComparison.InvariantCultureIgnoreCase);

			// Add the code and .csv
			filename = filename.Substring(1, x - 1);

			// Add the selected dimension
			if (Track.XY_Data)
			{
				if (Parameters.MLE_Dimension == 0) filename += "(X)";
				else filename += "(Y)";
			}
			else if (Track.LatLon_Data)
			{
				if (Parameters.MLE_Dimension == 0) filename += "(Long)";
				else filename += "(Lat)";
			}
			
			// Add the code indicating what analysis was performed
			if (p_Code.Length > 0) filename = filename + " " + p_Code;
			filename = filename + ".csv";
			return filename;
		}
	
	
		// Member functions
		public void WriteLine(string output)
		{
			try
	        {            
	            MyWriter.WriteLine(output);
	        }	catch (IOException) {}
		}
		
		public void Flush()
		{
			try
	        {            
	            MyWriter.Flush();
	        }	catch (IOException) {}
		}
			
			
		public void Close()
		{
			try {MyWriter.Close();}
			catch (IOException) {}
		}
		
		public bool	IsOK()	{return OK;}
	}
}
