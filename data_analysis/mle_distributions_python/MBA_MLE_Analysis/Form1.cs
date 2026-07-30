using System;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{
	public partial class Form1 : Form
	{
		Track MyTrack;
		bool HelpToggle = false;

		public Form1()
		{
			InitializeComponent();

			// Check the license
			MBA_Licence.MBA_Licence.CheckLicence(MBA_Licence.MBA_Licence.MLE_Analysis);

			if (!MBA_Licence.MBA_Licence.OK)
			{
				MessageBox.Show("This is a beta version of the MLE Analysis program and can only be used at the MBA\nunless you have a specific licence.", "MBA Licence error");
				b_MLE.Enabled = false;
				b_MLE_Quick.Enabled = false;
			}

			this.Text += " : " + Writer.Version;

			cb_MLE_Dist.SelectedIndex = 0;
			cb_MLE_Fitting.SelectedIndex = 0;
		}

		private void cb_MLE_Dist_selectedIndexChanged(Object source, EventArgs e)
		{
			Parameters.setMLE_Dist(cb_MLE_Dist);
			setMLE_AltDist();

			// Set the desccriptive labels
			if (Parameters.MLE_Dist == 0) l_exp.Text = "Mu";
            else if (Parameters.MLE_Dist == 1) l_exp.Text = "Lambda";
            else if (Parameters.MLE_Dist == 2) l_exp.Text = "Mu";
            else if (Parameters.MLE_Dist == 3) l_exp.Text = "Lambda";
            else if (Parameters.MLE_Dist == 4) l_exp.Text = "k / θ";
            else if (Parameters.MLE_Dist == 5) l_exp.Text = "Mean / S.D.";
        }

		// When the primary distribution is changed set the default alternate distribution
		private void setMLE_AltDist()
		{
			cb_MLE_AltDist.SelectedIndex = Parameters.MLE_AltDist;
		}

		private void cb_MLE_Discrete_checkedChanged(Object source, EventArgs e)
		{
			Parameters.MLE_Discrete = cb_MLE_Discrete.Checked;
		}

		private void cb_MLE_ptest_checkedChanged(Object source, EventArgs e)
		{
			Parameters.MLE_p_Test = cb_MLE_ptest.Checked;
		}

		private void cb_MLE_AltDist_selectedIndexChanged(Object source, EventArgs e)
		{
			Parameters.setMLE_AltDist(cb_MLE_AltDist);
		}

		private void cb_MLE_Fitting_SelectedIndexChanged(object sender, EventArgs e)
		{
			Parameters.MLE_Fitting = cb_MLE_Fitting.SelectedIndex;
		}

		private void cb_Coalesce_CheckedChanged(object sender, EventArgs e)
		{
			Parameters.Coalese = cb_Coalesce.Checked;
		}
	
		// Maximum likelihood estimators
		private void b_MLE_Quick_click(Object source, EventArgs e)
		{
			b_MLE_Quick.Enabled = false;
			b_MLE.Enabled = false;
			MLE(true);
			b_MLE_Quick.Enabled = true;
			b_MLE.Enabled = true;
		}

		private void b_MLE_click(Object source, EventArgs e)
		{
			b_MLE_Quick.Enabled = false;
			b_MLE.Enabled = false;
			MLE(false);
			b_MLE_Quick.Enabled = true;
			b_MLE.Enabled = true;
		}

		// Run the MLE analysis
		private void MLE(bool p_Quick)
		{
			if (MyTrack == null) return;
			if (MyTrack.getNoOfPoints() < 4) return;

			Cursor = Cursors.WaitCursor;
			l_Status.Text = "Running MLE analysis...";
			Application.DoEvents();
			Graph MyGraph = null;

			// Create the graph object, even if we dont need it
			string GraphText = "MLE Analysis - ";
			string GraphLabels = "X=log10 Step len, Y=log10 rank (Grey=Observations, Red=Best fit, Blue=Alt.)";

			if (Parameters.MLE_Dist == 0) GraphText = GraphText + "Power law";
			else if (Parameters.MLE_Dist == 1) GraphText = GraphText + "Exponential";
			else if (Parameters.MLE_Dist == 2) GraphText = GraphText + "Truncated Pareto";
			else if (Parameters.MLE_Dist == 3) GraphText = GraphText + "Truncated Exp.";
            else if (Parameters.MLE_Dist == 4) GraphText = GraphText + "Gamma";
            else if (Parameters.MLE_Dist == 5) GraphText = GraphText + "Log normal";

			MyGraph = new Graph(GraphText, GraphLabels);

			// Run the analysis
			MLE MyMLE = new MLE();
			MyMLE.Run(MyTrack, MyGraph, this, p_Quick);
			Cursor = Cursors.Default;

			if (!MyMLE.OK)
			{
				l_Status.Text = "MLE Analysis failed.";
				return;
			}

			// Display the graph if in quick mode
			if (p_Quick)
			{
				MyGraph.Show();
			}

			l_Status.Text = "Ready.";
		}

		private void m_ImportFile_Click(object sender, EventArgs e)
		{
			// Prompt for the file name
			if (OFD1.ShowDialog() == DialogResult.Cancel) return;

			m_ImportFile.Enabled = false;
			Cursor = Cursors.WaitCursor;
			ImportFile(OFD1.FileName);
			m_ImportFile.Enabled = true;
			Cursor = Cursors.Default;
		}

		private void ImportFile(string p_Filename)
		{
			if (!p_Filename.EndsWith(".csv"))
			{
				MessageBox.Show("Sorry, the import only accepts csv files", "Import error", MessageBoxButtons.OK, MessageBoxIcon.Error);
				return;
			}

			// Create the Track
			MyTrack = new Track(p_Filename);

			#region ClearFormFields
			l_Status.Text = "Importing file...";
			l_Filename.Text = string.Empty;
			l_Gaps.Text = string.Empty;
			l_MaxGap.Text = string.Empty;
			l_MaxStep.Text = string.Empty;
			l_MinGap.Text = string.Empty;
			l_MinStep.Text = string.Empty;
			l_MLE_AICw.Text = string.Empty;
			l_MLE_AltAICw.Text = string.Empty;
			l_MLE_AltGOF.Text = string.Empty;
			l_MLE_Exponent.Text = string.Empty;
			l_MLE_GOF.Text = string.Empty;
			l_MLE_p.Text = string.Empty;
			l_MLE_Xmax.Text = string.Empty;
			l_MLE_Xmin.Text = string.Empty;
			l_MLE_AICw.Text = string.Empty;
			l_MLE_AltAICw.Text = string.Empty;
			l_MLE_AltGOF.Text = string.Empty;
			l_MLE_Exponent.Text = string.Empty;
			l_MLE_GOF.Text = string.Empty;
			l_MLE_p.Text = string.Empty;
			l_MLE_Xmax.Text = string.Empty;
			l_MLE_Xmin.Text = string.Empty;
			l_Coalesed.Text = string.Empty;
			cb_Dimension.Items.Clear();
			#endregion

			Application.DoEvents();

			// Run the import
			if (!ImpSmartCSV.Import(MyTrack, this))
			{
				l_Status.Text = "Import failed.";
				MyTrack = null;
				return;
			}

			// Set up the dimension combo box
			if (Track.XY_Data)
			{
				cb_Dimension.Items.Add("X");
				cb_Dimension.Items.Add("Y");

				if (Track.Z_Data) cb_Dimension.Items.Add("Z");
			}
			else if (Track.LatLon_Data)
			{
				cb_Dimension.Items.Add("Long");
				cb_Dimension.Items.Add("Lat");
			}
			else if (Track.Depth_Data)
			{
				cb_Dimension.Items.Add("Depth");
			}
			else
			{
				cb_Dimension.Items.Add("Steps");
			}

			cb_Dimension.SelectedIndex = 0;

			l_Filename.Text = Track.Filename;
			l_Points.Text = MyTrack.getNoOfPoints().ToString();
			l_MinStep.Text = Parameters.RoundD(Track.MinStep);
			l_MaxStep.Text = Parameters.RoundD(Track.MaxStep);
			l_MinGap.Text = Track.MinGap.ToString();
			l_MaxGap.Text = Track.MaxGap.ToString();
			l_Status.Text = "Ready.";
		}

		// Implement drag and drop to automate a smart import
		private void panel1_DragDrop(object sender, DragEventArgs e)
		{
			string[] DroppedFileNames = new string[0];

			// Handle FileDrop data.
			if (e.Data.GetDataPresent(DataFormats.FileDrop))
			{
				// Assign the file names to a string array, in 
				// case the user has selected multiple files.
				try
				{
					DroppedFileNames = (string[])e.Data.GetData(DataFormats.FileDrop);
				}
				catch (Exception)
				{
					return;
				}
			}

			// We have a file to process
			Cursor = Cursors.WaitCursor;
			ImportFile(DroppedFileNames[0]);
			Cursor = Cursors.Default;
		}

		private void panel1_DragEnter(object sender, DragEventArgs e)
		{
			// If the data is a file
			if (e.Data.GetDataPresent(DataFormats.FileDrop))
			{
				e.Effect = DragDropEffects.Move;
			}
			else
			{
				e.Effect = DragDropEffects.None;
			}
		}

		// Set the selected dimension
		private void cb_Dimension_SelectedIndexChanged(object sender, EventArgs e)
		{
			Parameters.MLE_Dimension = cb_Dimension.SelectedIndex;
		}

		private void tb_MaxGap_Leave(object sender, EventArgs e)
		{
			Parameters.setMaxGap(tb_MaxGap);
		}

		private void aboutToolStripMenuItem_Click(object sender, EventArgs e)
		{
			About MyAbout = new About();
			MyAbout.ShowDialog();
		}

		private void enableToolTipsToolStripMenuItem_Click(object sender, EventArgs e)
		{
			HelpToggle = !HelpToggle;
			tt_Help.Active = HelpToggle;
		}
	}
}
