using System;
using System.Drawing;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{
	public partial class Graph : Form
	{
		// Member variables
		private	int			S1Point = 0,
							S2Point = 0,
							S3Point = 0,
							MaxPoints;
		
		private	double[]	XValues,
							YValues,
							X3Values,
							Y3Values,
							X2Values,
							Y2Values;
		
		private	double		MinX = Double.MaxValue,
							MaxX = -Double.MaxValue,
							MinY = Double.MaxValue,
							MaxY = -Double.MaxValue;	
		
		private	double		XOffset, YOffset, RangeX, RangeY, ScaleX, ScaleY;

		private bool		Lines = false,
							Points = false,
							Bars = false,
							Dots = true;
		
		// Graphics
		private Pen			S1Pen, S2Pen, S3Pen;
		private Bitmap		MyBitmap;
		private Graphics	PanelGraphics, g;
	
		public Graph(string p_Title, string p_Labels)
		{
			InitializeComponent();

			// Set default pens
			S1Pen = new Pen(Color.DarkGray);
			S2Pen = new Pen(Color.Red);
			S3Pen = new Pen(Color.Blue);
			PanelGraphics = p_Graph.CreateGraphics();

			// Set up labels
			this.Text = Track.getShortFileName();

			// Add the selected dimension
			if (Track.XY_Data)
			{
				if (Parameters.MLE_Dimension == 0) this.Text += " - X";
				else if (Parameters.MLE_Dimension == 1) this.Text += " - Y";
				else this.Text += " - Z";
			}
			else if (Track.LatLon_Data)
			{
				if (Parameters.MLE_Dimension == 0) this.Text += " - Long";
				else this.Text += " - Lat";
			}
			else if (Track.Step_Data)
			{
				this.Text += " - Steps";
			}
			else
			{
				this.Text += " - Depth";
			}

			l_Labels.Text = p_Labels;
		}

		// Create the arrays to hold the points
		public void set_Size(int p_MaxPoints)
		{
			MaxPoints = p_MaxPoints;
			XValues = new double[MaxPoints];
			YValues = new double[MaxPoints];
			X2Values = new double[MaxPoints];
			Y2Values = new double[MaxPoints];
			X3Values = new double[MaxPoints];
			Y3Values = new double[MaxPoints];
		}

		public void set_Size(double p_MaxPoints)
		{
			set_Size((int) p_MaxPoints);
		}
		
		// Add points to the array
		public void	add_Point(double x, double y) 
		{
			if (S1Point == MaxPoints)	return;
			
			XValues[S1Point] = x;
			YValues[S1Point] = y;
			S1Point++;
			setMinMax(x, y);
		}
		

		// Add points to series 2
		public void	add_Point2(double x, double y) 
		{
			if (S2Point == MaxPoints)	return;
			
			X2Values[S2Point] = x;
			Y2Values[S2Point] = y;
			S2Point++;
			setMinMax(x, y);
		}
		
		// Add points to series 3
		public void	add_Point3(double x, double y) 
		{
			if (S2Point == MaxPoints)	return;
			
			X3Values[S3Point] = x;
			Y3Values[S3Point] = y;
			S3Point++;
			setMinMax(x, y);
		}
		

		private void setMinMax(double x, double y)
		{
			// Set min & max values
			if (x < MinX) MinX = x;
			if (x > MaxX) MaxX = x;
			if (y < MinY) MinY = y;
			if (y > MaxY) MaxY = y;
		}

		// For convienience in adding points :)
		public void	add_Point(int x, double y) 
		{
			add_Point((double) x, y);
		}
		
		public void	add_Point(double x, int y) 
		{
			add_Point(x, (double) y);
		}

		public void	add_Point(int x, int y) 
		{
			add_Point((double) x, (double) y);
		}

		// For convienience in adding points :)
		public void	add_Point2(int x, double y) 
		{
			add_Point2((double) x, y);
		}
		
		public void	add_Point2(double x, int y) 
		{
			add_Point2(x, (double) y);
		}

		public void	add_Point2(int x, int y) 
		{
			add_Point2((double) x, (double) y);
		}
		
		// For convienience in adding points :)
		public void	add_Point3(int x, double y) 
		{
			add_Point3((double) x, y);
		}
		
		public void	add_Point3(double x, int y) 
		{
			add_Point3(x, (double) y);
		}

		public void	add_Point3(int x, int y) 
		{
			add_Point3((double) x, (double) y);
		}
		
		// Plot the graph
		//	Only do the drawing if the bitmap doesn't exist; i.e. at startup or following a resize event
		private void paint_Graph(bool p_ReDraw)
		{
			// Create graphics stuff, starting with the bitmap
			if (MyBitmap == null || p_ReDraw)
			{
				MyBitmap = new Bitmap(p_Graph.Width, p_Graph.Height);
				g = Graphics.FromImage(MyBitmap);
				g.Clear(Color.White);
				paint_Graph(g);
			}

			// Draw it to the panel
			PanelGraphics.DrawImage(MyBitmap, new Point(0, 0));
		}
			
		// Plot the graph
		private void paint_Graph(Graphics g)
		{
			int gap, BarWidth = 0;

			// If the Lines check box has been changed then clear the display
			if (rb_Lines.Checked != Lines
				|| rb_Points.Checked != Points
				|| rb_Dots.Checked != Dots
				|| rb_Bars.Checked != Bars)
			{
				g.Clear(Color.White);
				Lines = rb_Lines.Checked;
				Points = rb_Points.Checked;
				Dots = rb_Dots.Checked;
				Bars = rb_Bars.Checked;

				// If bars is selected then calculate a bar width from the minimum
				//	X interval
				if (Bars)
				{
					BarWidth = int.MaxValue;

					for (int i = 1; i < S1Point; i++)
					{
						gap = (int)XValues[i] - (int)XValues[i - 1];
						if (gap < BarWidth) BarWidth = gap;
					}

					if (BarWidth > 1) BarWidth -= 1;
				}
			}

			// Set scales and other graphics stuff
			RangeX = Math.Abs(MaxX - MinX);
			RangeY = Math.Abs(MaxY - MinY);

			if (RangeX == 0 || RangeY == 0) return;

			// Calculate scaling so that the points all fit in the panel, with a few pixel gap
			ScaleX = (p_Graph.Width - 9) / RangeX;
			ScaleY = (p_Graph.Height - 9) / RangeY;

			// Set the offsets
			XOffset = (int)(MinX * ScaleX) - 3;
			YOffset = (int)(MinY * ScaleY) - 6;	// For some reason setting this to -3 is insufficient

			// TODO: Draw scales

			// Plot the points for Series 1
			Points = true;
			Dots = Lines = false;
			if (S1Point > 0) PlotSeries(g, XValues, YValues, S1Point, S1Pen);

			// Plot the points for Series 2
			Lines = true;
			Points = false;
			if (S2Point > 0) PlotSeries(g, X2Values, Y2Values, S2Point, S2Pen);

			// Plot the points for Series 2
			if (S3Point > 0) PlotSeries(g, X3Values, Y3Values, S3Point, S3Pen);
		}


		// Plot the points for a Series - remember that y is measured Down from the Top!
		private void PlotSeries(Graphics g, double[] p_XValues, double[] p_YValues, int p_Points, Pen p_Pen)
		{
			int x, y, ox = 0, oy = 0;
			SolidBrush MyBrush = null;

			if (Dots) MyBrush = new SolidBrush(p_Pen.Color);

			try
			{
				for (int i = 0; i < p_Points; i++)
				{
					x = (int)((p_XValues[i] * ScaleX) - XOffset);
					y = p_Graph.Height - (int)((p_YValues[i] * ScaleY) - YOffset);

					if (i > 0 && Lines) g.DrawLine(p_Pen, ox, oy, x, y);
					else if (Bars) g.DrawLine(p_Pen, x, y, x, p_Graph.Height);
					else if (Points) g.DrawRectangle(p_Pen, x-1, y-1, 2, 2);
					else if (Dots) g.FillRectangle(MyBrush, x, y, 1, 1);

					ox = x;
					oy = y;
				}
			}
			catch (Exception) { }
		}

		private void p_Graph_paint(Object source, PaintEventArgs e)
		{
			// Draw the image to the bitmap
			paint_Graph(false);
		}
		
		private void rb_Dots_Click(object sender, EventArgs e)
		{
			paint_Graph(true);
		}

		private void rb_Bars_Click(object sender, EventArgs e)
		{
			paint_Graph(true);
		}

		private void rb_Lines_Click(object sender, EventArgs e)
		{
			paint_Graph(true);
		}

		private void rb_Points_Click(object sender, EventArgs e)
		{
			paint_Graph(true);
		}

		public void set_Lines(bool p)
		{
			rb_Lines.Checked = p;
		}

		public void set_Bars(bool p)
		{
			rb_Bars.Checked = p;
		}
		public void set_Points(bool p)
		{
			rb_Points.Checked = p;
		}
		
		public void set_Dots(bool p)
		{
			rb_Dots.Checked = p;
		}
				
		
		// Generate a bitmap from the screen plot
		private void BitmapToClipboard()
		{
			// Create the bitmap
			Bitmap ZBitmap = new Bitmap(MyBitmap);
			Graphics bmg = Graphics.FromImage(ZBitmap);
			
			Pen Black = new Pen(Color.Black);

			// Draw the border
			bmg.DrawLine(Black, 0, 0, ZBitmap.Width - 1, 0);
			bmg.DrawLine(Black, ZBitmap.Width - 1, 0, ZBitmap.Width - 1, ZBitmap.Height - 1);
			bmg.DrawLine(Black, ZBitmap.Width - 1, ZBitmap.Height - 1, 0, ZBitmap.Height - 1);
			bmg.DrawLine(Black, 0, ZBitmap.Height - 1, 0, 0);

			DataObject MyObj = new DataObject(DataFormats.Bitmap, ZBitmap);
			Clipboard.SetDataObject((IDataObject)MyObj, true);
		}	

		private void p_Graph_leave(Object source, EventArgs e)
		{
			try {toolTip1.Active = false;}
			catch (Exception){};
		}

		private void p_Graph_mouseDown(Object source, MouseEventArgs e)
		{
			// Calculate the x & y values
			double x = (e.X + XOffset) / ScaleX;
			double y = ((p_Graph.Height - e.Y) + YOffset) / ScaleY;

			// Display the values
			toolTip1.SetToolTip(p_Graph, "X=" + x.ToString("F3") + "\nY=" + y.ToString("F3"));
			toolTip1.Active = true;
			toolTip1.InitialDelay = 0;
		}

		private void copyImageToClipboardToolStripMenuItem_Click(object sender, EventArgs e)
		{
			BitmapToClipboard();
		}

         private void p_Graph_Paint(object sender, PaintEventArgs e)
        {
            MyBitmap = null;
            PanelGraphics = p_Graph.CreateGraphics();
            paint_Graph(true);
        }
	}
}
