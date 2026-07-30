namespace MBA_MLE_Analysis
{
	partial class Graph
	{
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		/// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null))
			{
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region Windows Form Designer generated code

		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Graph));
            this.p_Graph = new System.Windows.Forms.Panel();
            this.cm_Display = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.copyImageToClipboardToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.rb_Bars = new System.Windows.Forms.RadioButton();
            this.rb_Lines = new System.Windows.Forms.RadioButton();
            this.rb_Dots = new System.Windows.Forms.RadioButton();
            this.rb_Points = new System.Windows.Forms.RadioButton();
            this.l_Labels = new System.Windows.Forms.Label();
            this.toolTip1 = new System.Windows.Forms.ToolTip(this.components);
            this.p_Graph.SuspendLayout();
            this.cm_Display.SuspendLayout();
            this.groupBox1.SuspendLayout();
            this.SuspendLayout();
            // 
            // p_Graph
            // 
            this.p_Graph.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.p_Graph.BackColor = System.Drawing.Color.White;
            this.p_Graph.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.p_Graph.ContextMenuStrip = this.cm_Display;
            this.p_Graph.Controls.Add(this.groupBox1);
            this.p_Graph.Location = new System.Drawing.Point(12, 12);
            this.p_Graph.Name = "p_Graph";
            this.p_Graph.Size = new System.Drawing.Size(378, 222);
            this.p_Graph.TabIndex = 0;
            this.p_Graph.Text = "panel1";
            this.p_Graph.MouseLeave += new System.EventHandler(this.p_Graph_leave);
            this.p_Graph.Paint += new System.Windows.Forms.PaintEventHandler(this.p_Graph_paint);
            this.p_Graph.Leave += new System.EventHandler(this.p_Graph_leave);
            this.p_Graph.MouseDown += new System.Windows.Forms.MouseEventHandler(this.p_Graph_mouseDown);
            // 
            // cm_Display
            // 
            this.cm_Display.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.copyImageToClipboardToolStripMenuItem});
            this.cm_Display.Name = "cm_Display";
            this.cm_Display.Size = new System.Drawing.Size(206, 26);
            // 
            // copyImageToClipboardToolStripMenuItem
            // 
            this.copyImageToClipboardToolStripMenuItem.Image = ((System.Drawing.Image)(resources.GetObject("copyImageToClipboardToolStripMenuItem.Image")));
            this.copyImageToClipboardToolStripMenuItem.Name = "copyImageToClipboardToolStripMenuItem";
            this.copyImageToClipboardToolStripMenuItem.Size = new System.Drawing.Size(205, 22);
            this.copyImageToClipboardToolStripMenuItem.Text = "Copy image to clipboard";
            this.copyImageToClipboardToolStripMenuItem.Click += new System.EventHandler(this.copyImageToClipboardToolStripMenuItem_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox1.Controls.Add(this.rb_Bars);
            this.groupBox1.Controls.Add(this.rb_Lines);
            this.groupBox1.Controls.Add(this.rb_Dots);
            this.groupBox1.Controls.Add(this.rb_Points);
            this.groupBox1.Location = new System.Drawing.Point(307, 3);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(66, 110);
            this.groupBox1.TabIndex = 7;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Controls";
            this.groupBox1.Visible = false;
            // 
            // rb_Bars
            // 
            this.rb_Bars.AutoSize = true;
            this.rb_Bars.Location = new System.Drawing.Point(6, 88);
            this.rb_Bars.Name = "rb_Bars";
            this.rb_Bars.Size = new System.Drawing.Size(46, 17);
            this.rb_Bars.TabIndex = 3;
            this.rb_Bars.Text = "Bars";
            this.rb_Bars.UseVisualStyleBackColor = true;
            this.rb_Bars.Click += new System.EventHandler(this.rb_Bars_Click);
            // 
            // rb_Lines
            // 
            this.rb_Lines.AutoSize = true;
            this.rb_Lines.Location = new System.Drawing.Point(6, 65);
            this.rb_Lines.Name = "rb_Lines";
            this.rb_Lines.Size = new System.Drawing.Size(50, 17);
            this.rb_Lines.TabIndex = 2;
            this.rb_Lines.Text = "Lines";
            this.rb_Lines.UseVisualStyleBackColor = true;
            this.rb_Lines.Click += new System.EventHandler(this.rb_Lines_Click);
            // 
            // rb_Dots
            // 
            this.rb_Dots.AutoSize = true;
            this.rb_Dots.Checked = true;
            this.rb_Dots.Location = new System.Drawing.Point(6, 42);
            this.rb_Dots.Name = "rb_Dots";
            this.rb_Dots.Size = new System.Drawing.Size(47, 17);
            this.rb_Dots.TabIndex = 1;
            this.rb_Dots.TabStop = true;
            this.rb_Dots.Text = "Dots";
            this.rb_Dots.UseVisualStyleBackColor = true;
            this.rb_Dots.Click += new System.EventHandler(this.rb_Dots_Click);
            // 
            // rb_Points
            // 
            this.rb_Points.AutoSize = true;
            this.rb_Points.Location = new System.Drawing.Point(6, 19);
            this.rb_Points.Name = "rb_Points";
            this.rb_Points.Size = new System.Drawing.Size(54, 17);
            this.rb_Points.TabIndex = 0;
            this.rb_Points.Text = "Points";
            this.rb_Points.UseVisualStyleBackColor = true;
            this.rb_Points.Click += new System.EventHandler(this.rb_Points_Click);
            // 
            // l_Labels
            // 
            this.l_Labels.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.l_Labels.AutoEllipsis = true;
            this.l_Labels.AutoSize = true;
            this.l_Labels.Location = new System.Drawing.Point(13, 240);
            this.l_Labels.Name = "l_Labels";
            this.l_Labels.Size = new System.Drawing.Size(34, 13);
            this.l_Labels.TabIndex = 3;
            this.l_Labels.Text = "labels";
            // 
            // toolTip1
            // 
            this.toolTip1.IsBalloon = true;
            // 
            // Graph
            // 
            this.AutoScaleBaseSize = new System.Drawing.Size(5, 13);
            this.ClientSize = new System.Drawing.Size(402, 259);
            this.Controls.Add(this.p_Graph);
            this.Controls.Add(this.l_Labels);
            this.MinimumSize = new System.Drawing.Size(410, 293);
            this.Name = "Graph";
            this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Show;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Paint += new System.Windows.Forms.PaintEventHandler(this.p_Graph_Paint);
            this.p_Graph.ResumeLayout(false);
            this.cm_Display.ResumeLayout(false);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

		}

		#endregion

		internal System.Windows.Forms.Label l_Labels;
		internal System.Windows.Forms.Panel p_Graph;
		private System.Windows.Forms.ToolTip toolTip1;
		private System.Windows.Forms.ContextMenuStrip cm_Display;
		private System.Windows.Forms.ToolStripMenuItem copyImageToClipboardToolStripMenuItem;
		private System.Windows.Forms.GroupBox groupBox1;
		private System.Windows.Forms.RadioButton rb_Bars;
		private System.Windows.Forms.RadioButton rb_Lines;
		private System.Windows.Forms.RadioButton rb_Dots;
		private System.Windows.Forms.RadioButton rb_Points;
	}
}