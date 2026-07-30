namespace MBA_MLE_Analysis
{
	partial class Form1
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.OFD1 = new System.Windows.Forms.OpenFileDialog();
            this.pb_Progress = new System.Windows.Forms.ProgressBar();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.l_MaxGap = new System.Windows.Forms.Label();
            this.l_MinGap = new System.Windows.Forms.Label();
            this.l_MaxStep = new System.Windows.Forms.Label();
            this.l_MinStep = new System.Windows.Forms.Label();
            this.l_Points = new System.Windows.Forms.Label();
            this.l_Filename = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.label7 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.l3 = new System.Windows.Forms.Label();
            this.l2 = new System.Windows.Forms.Label();
            this.l1 = new System.Windows.Forms.Label();
            this.cb_MLE_Fitting = new System.Windows.Forms.ComboBox();
            this.cb_Coalesce = new System.Windows.Forms.CheckBox();
            this.cb_MLE_Discrete = new System.Windows.Forms.CheckBox();
            this.cb_MLE_ptest = new System.Windows.Forms.CheckBox();
            this.tb_MaxGap = new System.Windows.Forms.TextBox();
            this.cb_Dimension = new System.Windows.Forms.ComboBox();
            this.cb_MLE_AltDist = new System.Windows.Forms.ComboBox();
            this.cb_MLE_Dist = new System.Windows.Forms.ComboBox();
            this.l_MLE_AltAICw = new System.Windows.Forms.Label();
            this.l_MLE_AICw = new System.Windows.Forms.Label();
            this.l_MLE_AltGOF = new System.Windows.Forms.Label();
            this.l_MLE_p = new System.Windows.Forms.Label();
            this.l_MLE_Xmax = new System.Windows.Forms.Label();
            this.l_MLE_GOF = new System.Windows.Forms.Label();
            this.l_MLE_Xmin = new System.Windows.Forms.Label();
            this.l_MLE_Exponent = new System.Windows.Forms.Label();
            this.b_MLE_Quick = new System.Windows.Forms.Button();
            this.b_MLE = new System.Windows.Forms.Button();
            this.l_Status = new System.Windows.Forms.Label();
            this.l_Gaps = new System.Windows.Forms.Label();
            this.l_Coalesed = new System.Windows.Forms.Label();
            this.groupBox17 = new System.Windows.Forms.GroupBox();
            this.label58 = new System.Windows.Forms.Label();
            this.groupBox4 = new System.Windows.Forms.GroupBox();
            this.label6 = new System.Windows.Forms.Label();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label48 = new System.Windows.Forms.Label();
            this.label54 = new System.Windows.Forms.Label();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.label4 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label63 = new System.Windows.Forms.Label();
            this.label61 = new System.Windows.Forms.Label();
            this.label60 = new System.Windows.Forms.Label();
            this.label46 = new System.Windows.Forms.Label();
            this.label62 = new System.Windows.Forms.Label();
            this.label59 = new System.Windows.Forms.Label();
            this.l_xmin = new System.Windows.Forms.Label();
            this.l_exp = new System.Windows.Forms.Label();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.importFileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.m_ImportFile = new System.Windows.Forms.ToolStripMenuItem();
            this.helpToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.enableToolTipsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.aboutToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.tt_Help = new System.Windows.Forms.ToolTip(this.components);
            this.groupBox1.SuspendLayout();
            this.groupBox17.SuspendLayout();
            this.groupBox4.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // OFD1
            // 
            this.OFD1.Filter = "CSV Files|*.csv";
            // 
            // pb_Progress
            // 
            this.pb_Progress.Location = new System.Drawing.Point(6, 232);
            this.pb_Progress.Name = "pb_Progress";
            this.pb_Progress.Size = new System.Drawing.Size(682, 13);
            this.pb_Progress.TabIndex = 1;
            this.pb_Progress.Tag = "";
            this.tt_Help.SetToolTip(this.pb_Progress, "Progress!");
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.l_MaxGap);
            this.groupBox1.Controls.Add(this.l_MinGap);
            this.groupBox1.Controls.Add(this.l_MaxStep);
            this.groupBox1.Controls.Add(this.l_MinStep);
            this.groupBox1.Controls.Add(this.l_Points);
            this.groupBox1.Controls.Add(this.l_Filename);
            this.groupBox1.Controls.Add(this.label8);
            this.groupBox1.Controls.Add(this.label7);
            this.groupBox1.Controls.Add(this.label5);
            this.groupBox1.Controls.Add(this.l3);
            this.groupBox1.Controls.Add(this.l2);
            this.groupBox1.Controls.Add(this.l1);
            this.groupBox1.Location = new System.Drawing.Point(12, 27);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(697, 74);
            this.groupBox1.TabIndex = 2;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "File details";
            this.tt_Help.SetToolTip(this.groupBox1, "Import csv files into the program using the File/Import menu option, or by draggi" +
                    "ng and dropping the file anywhere on the form");
            // 
            // l_MaxGap
            // 
            this.l_MaxGap.AutoEllipsis = true;
            this.l_MaxGap.BackColor = System.Drawing.SystemColors.Window;
            this.l_MaxGap.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MaxGap.Location = new System.Drawing.Point(629, 42);
            this.l_MaxGap.Margin = new System.Windows.Forms.Padding(3);
            this.l_MaxGap.Name = "l_MaxGap";
            this.l_MaxGap.Size = new System.Drawing.Size(52, 20);
            this.l_MaxGap.TabIndex = 17;
            this.l_MaxGap.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MaxGap, "The maximum track gap (time interval) between successive data points");
            // 
            // l_MinGap
            // 
            this.l_MinGap.AutoEllipsis = true;
            this.l_MinGap.BackColor = System.Drawing.SystemColors.Window;
            this.l_MinGap.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MinGap.Location = new System.Drawing.Point(517, 42);
            this.l_MinGap.Margin = new System.Windows.Forms.Padding(3);
            this.l_MinGap.Name = "l_MinGap";
            this.l_MinGap.Size = new System.Drawing.Size(52, 20);
            this.l_MinGap.TabIndex = 16;
            this.l_MinGap.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MinGap, "The minimum track gap (time interval) between successive data points");
            // 
            // l_MaxStep
            // 
            this.l_MaxStep.AutoEllipsis = true;
            this.l_MaxStep.BackColor = System.Drawing.SystemColors.Window;
            this.l_MaxStep.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MaxStep.Location = new System.Drawing.Point(365, 42);
            this.l_MaxStep.Margin = new System.Windows.Forms.Padding(3);
            this.l_MaxStep.Name = "l_MaxStep";
            this.l_MaxStep.Size = new System.Drawing.Size(95, 20);
            this.l_MaxStep.TabIndex = 15;
            this.l_MaxStep.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MaxStep, "The maximum step-length computed from the imported data");
            // 
            // l_MinStep
            // 
            this.l_MinStep.AutoEllipsis = true;
            this.l_MinStep.BackColor = System.Drawing.SystemColors.Window;
            this.l_MinStep.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MinStep.Location = new System.Drawing.Point(205, 42);
            this.l_MinStep.Margin = new System.Windows.Forms.Padding(3);
            this.l_MinStep.Name = "l_MinStep";
            this.l_MinStep.Size = new System.Drawing.Size(98, 20);
            this.l_MinStep.TabIndex = 14;
            this.l_MinStep.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MinStep, "The minimum step-length computed from the imported data");
            // 
            // l_Points
            // 
            this.l_Points.AutoEllipsis = true;
            this.l_Points.BackColor = System.Drawing.SystemColors.Window;
            this.l_Points.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_Points.Location = new System.Drawing.Point(91, 42);
            this.l_Points.Margin = new System.Windows.Forms.Padding(3);
            this.l_Points.Name = "l_Points";
            this.l_Points.Size = new System.Drawing.Size(55, 20);
            this.l_Points.TabIndex = 13;
            this.l_Points.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_Points, "The number of data points imported from the csv file. \r\nThe number of move step-l" +
                    "engths will be 1 less than this.");
            // 
            // l_Filename
            // 
            this.l_Filename.AutoEllipsis = true;
            this.l_Filename.BackColor = System.Drawing.SystemColors.Window;
            this.l_Filename.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_Filename.CausesValidation = false;
            this.l_Filename.Location = new System.Drawing.Point(91, 16);
            this.l_Filename.Margin = new System.Windows.Forms.Padding(3);
            this.l_Filename.Name = "l_Filename";
            this.l_Filename.Size = new System.Drawing.Size(591, 20);
            this.l_Filename.TabIndex = 12;
            this.l_Filename.Tag = "";
            this.l_Filename.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(309, 46);
            this.label8.Margin = new System.Windows.Forms.Padding(3);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(50, 13);
            this.label8.TabIndex = 11;
            this.label8.Text = "Max step";
            this.label8.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(152, 46);
            this.label7.Margin = new System.Windows.Forms.Padding(3);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(47, 13);
            this.label7.TabIndex = 10;
            this.label7.Text = "Min step";
            this.label7.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(466, 46);
            this.label5.Margin = new System.Windows.Forms.Padding(3);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(45, 13);
            this.label5.TabIndex = 9;
            this.label5.Text = "Min gap";
            this.label5.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // l3
            // 
            this.l3.AutoSize = true;
            this.l3.Location = new System.Drawing.Point(575, 46);
            this.l3.Margin = new System.Windows.Forms.Padding(3);
            this.l3.Name = "l3";
            this.l3.Size = new System.Drawing.Size(48, 13);
            this.l3.TabIndex = 8;
            this.l3.Text = "Max gap";
            this.l3.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // l2
            // 
            this.l2.AutoSize = true;
            this.l2.Location = new System.Drawing.Point(6, 46);
            this.l2.Margin = new System.Windows.Forms.Padding(3);
            this.l2.Name = "l2";
            this.l2.Size = new System.Drawing.Size(79, 13);
            this.l2.TabIndex = 7;
            this.l2.Text = "Imported points";
            this.l2.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // l1
            // 
            this.l1.AutoSize = true;
            this.l1.Location = new System.Drawing.Point(6, 20);
            this.l1.Margin = new System.Windows.Forms.Padding(3);
            this.l1.Name = "l1";
            this.l1.Size = new System.Drawing.Size(52, 13);
            this.l1.TabIndex = 1;
            this.l1.Text = "File name";
            this.l1.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            this.tt_Help.SetToolTip(this.l1, "The name and path of the imported file.");
            // 
            // cb_MLE_Fitting
            // 
            this.cb_MLE_Fitting.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cb_MLE_Fitting.FormattingEnabled = true;
            this.cb_MLE_Fitting.Items.AddRange(new object[] {
            "Limited",
            "No fitting",
            "Best fit Xmin"});
            this.cb_MLE_Fitting.Location = new System.Drawing.Point(236, 20);
            this.cb_MLE_Fitting.Name = "cb_MLE_Fitting";
            this.cb_MLE_Fitting.Size = new System.Drawing.Size(95, 21);
            this.cb_MLE_Fitting.TabIndex = 0;
            this.cb_MLE_Fitting.Tag = "";
            this.tt_Help.SetToolTip(this.cb_MLE_Fitting, "Set options for the fitting of Xmin and Xmax\r\nLimited searches until 5 worse fitt" +
                    "ing values are found.\r\nBest fit searches all possible values.");
            this.cb_MLE_Fitting.SelectedIndexChanged += new System.EventHandler(this.cb_MLE_Fitting_SelectedIndexChanged);
            // 
            // cb_Coalesce
            // 
            this.cb_Coalesce.AutoSize = true;
            this.cb_Coalesce.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.cb_Coalesce.Location = new System.Drawing.Point(337, 22);
            this.cb_Coalesce.Name = "cb_Coalesce";
            this.cb_Coalesce.Size = new System.Drawing.Size(70, 17);
            this.cb_Coalesce.TabIndex = 1;
            this.cb_Coalesce.Tag = "";
            this.cb_Coalesce.Text = "Coalesce";
            this.tt_Help.SetToolTip(this.cb_Coalesce, "Check this box to coalesce steps that form part of a continuous movement into a s" +
                    "ingle step.\r\nThis is important for the correct analysis of data projected into 1" +
                    "D.");
            this.cb_Coalesce.UseVisualStyleBackColor = true;
            this.cb_Coalesce.CheckedChanged += new System.EventHandler(this.cb_Coalesce_CheckedChanged);
            // 
            // cb_MLE_Discrete
            // 
            this.cb_MLE_Discrete.AutoSize = true;
            this.cb_MLE_Discrete.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.cb_MLE_Discrete.Location = new System.Drawing.Point(413, 22);
            this.cb_MLE_Discrete.Name = "cb_MLE_Discrete";
            this.cb_MLE_Discrete.Size = new System.Drawing.Size(65, 17);
            this.cb_MLE_Discrete.TabIndex = 2;
            this.cb_MLE_Discrete.Tag = "";
            this.cb_MLE_Discrete.Text = "Discrete";
            this.tt_Help.SetToolTip(this.cb_MLE_Discrete, "Check this box to perform the tests using discrete data where all values \r\nare so" +
                    "me multiple of the minimum observed value.");
            this.cb_MLE_Discrete.CheckedChanged += new System.EventHandler(this.cb_MLE_Discrete_checkedChanged);
            // 
            // cb_MLE_ptest
            // 
            this.cb_MLE_ptest.AutoSize = true;
            this.cb_MLE_ptest.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.cb_MLE_ptest.Location = new System.Drawing.Point(484, 22);
            this.cb_MLE_ptest.Name = "cb_MLE_ptest";
            this.cb_MLE_ptest.Size = new System.Drawing.Size(52, 17);
            this.cb_MLE_ptest.TabIndex = 3;
            this.cb_MLE_ptest.Tag = "";
            this.cb_MLE_ptest.Text = "p-test";
            this.tt_Help.SetToolTip(this.cb_MLE_ptest, resources.GetString("cb_MLE_ptest.ToolTip"));
            this.cb_MLE_ptest.CheckedChanged += new System.EventHandler(this.cb_MLE_ptest_checkedChanged);
            // 
            // tb_MaxGap
            // 
            this.tb_MaxGap.Location = new System.Drawing.Point(137, 20);
            this.tb_MaxGap.Name = "tb_MaxGap";
            this.tb_MaxGap.Size = new System.Drawing.Size(52, 20);
            this.tb_MaxGap.TabIndex = 2;
            this.tb_MaxGap.Tag = "";
            this.tb_MaxGap.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            this.tt_Help.SetToolTip(this.tb_MaxGap, "Enter the maximum allowed track gap in the format hh:mm:ss\r\n or just seconds (15)" +
                    ", or just minutes and seconds (12:22).\r\nSteps spanning gaps greater than this wi" +
                    "ll be ignored.");
            this.tb_MaxGap.Leave += new System.EventHandler(this.tb_MaxGap_Leave);
            // 
            // cb_Dimension
            // 
            this.cb_Dimension.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cb_Dimension.FormattingEnabled = true;
            this.cb_Dimension.Location = new System.Drawing.Point(470, 19);
            this.cb_Dimension.Name = "cb_Dimension";
            this.cb_Dimension.Size = new System.Drawing.Size(71, 21);
            this.cb_Dimension.TabIndex = 2;
            this.cb_Dimension.Tag = "";
            this.tt_Help.SetToolTip(this.cb_Dimension, "If more than one dimension has been imported select which to analyse from this li" +
                    "st.");
            this.cb_Dimension.SelectedIndexChanged += new System.EventHandler(this.cb_Dimension_SelectedIndexChanged);
            // 
            // cb_MLE_AltDist
            // 
            this.cb_MLE_AltDist.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cb_MLE_AltDist.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.cb_MLE_AltDist.Items.AddRange(new object[] {
            "Power",
            "Exponential",
            "Truncated Pareto",
            "Truncated Exponential"});
            this.cb_MLE_AltDist.Location = new System.Drawing.Point(267, 19);
            this.cb_MLE_AltDist.Name = "cb_MLE_AltDist";
            this.cb_MLE_AltDist.Size = new System.Drawing.Size(135, 21);
            this.cb_MLE_AltDist.TabIndex = 1;
            this.cb_MLE_AltDist.Tag = "";
            this.tt_Help.SetToolTip(this.cb_MLE_AltDist, "Select the distribution to be used as a model comparison\r\ni.e. the Alternate dist" +
                    "ribution");
            this.cb_MLE_AltDist.SelectedIndexChanged += new System.EventHandler(this.cb_MLE_AltDist_selectedIndexChanged);
            // 
            // cb_MLE_Dist
            // 
            this.cb_MLE_Dist.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cb_MLE_Dist.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.cb_MLE_Dist.Items.AddRange(new object[] {
            "Power",
            "Exponential",
            "Truncated Pareto",
            "Truncated exponential"});
            this.cb_MLE_Dist.Location = new System.Drawing.Point(71, 19);
            this.cb_MLE_Dist.Name = "cb_MLE_Dist";
            this.cb_MLE_Dist.Size = new System.Drawing.Size(135, 21);
            this.cb_MLE_Dist.TabIndex = 0;
            this.cb_MLE_Dist.Tag = "";
            this.tt_Help.SetToolTip(this.cb_MLE_Dist, "Select the primary distribution to test against the empirical data.\r\nUse the alte" +
                    "rnate drop down list (right) to override the default alternate distribution.");
            this.cb_MLE_Dist.SelectedIndexChanged += new System.EventHandler(this.cb_MLE_Dist_selectedIndexChanged);
            // 
            // l_MLE_AltAICw
            // 
            this.l_MLE_AltAICw.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_AltAICw.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_AltAICw.Location = new System.Drawing.Point(566, 55);
            this.l_MLE_AltAICw.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_AltAICw.Name = "l_MLE_AltAICw";
            this.l_MLE_AltAICw.Size = new System.Drawing.Size(48, 20);
            this.l_MLE_AltAICw.TabIndex = 77;
            this.l_MLE_AltAICw.Tag = "";
            this.l_MLE_AltAICw.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_AltAICw, "The Akaike weight calculated for the alternate distribution.\r\nA value of 1 indica" +
                    "tes full support, 0 indicates no support\r\nfor the tested distribution.\r\n");
            // 
            // l_MLE_AICw
            // 
            this.l_MLE_AICw.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_AICw.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_AICw.Location = new System.Drawing.Point(512, 55);
            this.l_MLE_AICw.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_AICw.Name = "l_MLE_AICw";
            this.l_MLE_AICw.Size = new System.Drawing.Size(48, 20);
            this.l_MLE_AICw.TabIndex = 78;
            this.l_MLE_AICw.Tag = "";
            this.l_MLE_AICw.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_AICw, "The Akaike weight calculated for the primary distribution.\r\nA value of 1 indicate" +
                    "s full support, 0 indicates no support\r\nfor the tested distribution.");
            // 
            // l_MLE_AltGOF
            // 
            this.l_MLE_AltGOF.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_AltGOF.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_AltGOF.Location = new System.Drawing.Point(448, 55);
            this.l_MLE_AltGOF.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_AltGOF.Name = "l_MLE_AltGOF";
            this.l_MLE_AltGOF.Size = new System.Drawing.Size(48, 20);
            this.l_MLE_AltGOF.TabIndex = 79;
            this.l_MLE_AltGOF.Tag = "";
            this.l_MLE_AltGOF.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_AltGOF, "GOF for the Alternate distribution.");
            // 
            // l_MLE_p
            // 
            this.l_MLE_p.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_p.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_p.Location = new System.Drawing.Point(627, 55);
            this.l_MLE_p.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_p.Name = "l_MLE_p";
            this.l_MLE_p.Size = new System.Drawing.Size(48, 20);
            this.l_MLE_p.TabIndex = 80;
            this.l_MLE_p.Tag = "";
            this.l_MLE_p.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_p, resources.GetString("l_MLE_p.ToolTip"));
            // 
            // l_MLE_Xmax
            // 
            this.l_MLE_Xmax.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_Xmax.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_Xmax.Location = new System.Drawing.Point(292, 55);
            this.l_MLE_Xmax.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_Xmax.Name = "l_MLE_Xmax";
            this.l_MLE_Xmax.Size = new System.Drawing.Size(80, 20);
            this.l_MLE_Xmax.TabIndex = 81;
            this.l_MLE_Xmax.Tag = "";
            this.l_MLE_Xmax.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_Xmax, "The estimated best fit Xmax (upper truncation) value.");
            // 
            // l_MLE_GOF
            // 
            this.l_MLE_GOF.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_GOF.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_GOF.Location = new System.Drawing.Point(394, 55);
            this.l_MLE_GOF.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_GOF.Name = "l_MLE_GOF";
            this.l_MLE_GOF.Size = new System.Drawing.Size(48, 20);
            this.l_MLE_GOF.TabIndex = 82;
            this.l_MLE_GOF.Tag = "";
            this.l_MLE_GOF.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_GOF, "Goodness of fit.T\r\nhe Kolmogorov-Smirnov D statistic, low values indicate better " +
                    "fits.");
            // 
            // l_MLE_Xmin
            // 
            this.l_MLE_Xmin.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_Xmin.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_Xmin.Location = new System.Drawing.Point(206, 55);
            this.l_MLE_Xmin.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_Xmin.Name = "l_MLE_Xmin";
            this.l_MLE_Xmin.Size = new System.Drawing.Size(80, 20);
            this.l_MLE_Xmin.TabIndex = 83;
            this.l_MLE_Xmin.Tag = "";
            this.l_MLE_Xmin.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_Xmin, "The estimated best fit Xmin (lower truncation) value.");
            // 
            // l_MLE_Exponent
            // 
            this.l_MLE_Exponent.AutoEllipsis = true;
            this.l_MLE_Exponent.BackColor = System.Drawing.SystemColors.Window;
            this.l_MLE_Exponent.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_MLE_Exponent.Location = new System.Drawing.Point(133, 55);
            this.l_MLE_Exponent.Margin = new System.Windows.Forms.Padding(3);
            this.l_MLE_Exponent.Name = "l_MLE_Exponent";
            this.l_MLE_Exponent.Size = new System.Drawing.Size(67, 20);
            this.l_MLE_Exponent.TabIndex = 84;
            this.l_MLE_Exponent.Tag = "";
            this.l_MLE_Exponent.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_MLE_Exponent, "The estimated exponent i.e. mu for power or truncated power law distributions\r\nor" +
                    " lambda for exponential or truncated exponential distributions.");
            // 
            // b_MLE_Quick
            // 
            this.b_MLE_Quick.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.b_MLE_Quick.Location = new System.Drawing.Point(618, 19);
            this.b_MLE_Quick.Name = "b_MLE_Quick";
            this.b_MLE_Quick.Size = new System.Drawing.Size(64, 23);
            this.b_MLE_Quick.TabIndex = 2;
            this.b_MLE_Quick.Tag = "";
            this.b_MLE_Quick.Text = "Quick";
            this.tt_Help.SetToolTip(this.b_MLE_Quick, "Run the analysis and display the results in a graph.");
            this.b_MLE_Quick.Click += new System.EventHandler(this.b_MLE_Quick_click);
            // 
            // b_MLE
            // 
            this.b_MLE.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.b_MLE.Location = new System.Drawing.Point(618, 49);
            this.b_MLE.Name = "b_MLE";
            this.b_MLE.Size = new System.Drawing.Size(64, 23);
            this.b_MLE.TabIndex = 3;
            this.b_MLE.Tag = "";
            this.b_MLE.Text = "Output";
            this.tt_Help.SetToolTip(this.b_MLE, resources.GetString("b_MLE.ToolTip"));
            this.b_MLE.Click += new System.EventHandler(this.b_MLE_click);
            // 
            // l_Status
            // 
            this.l_Status.AutoSize = true;
            this.l_Status.Location = new System.Drawing.Point(12, 362);
            this.l_Status.Name = "l_Status";
            this.l_Status.Size = new System.Drawing.Size(41, 13);
            this.l_Status.TabIndex = 4;
            this.l_Status.Tag = "";
            this.l_Status.Text = "Ready.";
            this.tt_Help.SetToolTip(this.l_Status, "An informational message describing the current activity.");
            // 
            // l_Gaps
            // 
            this.l_Gaps.BackColor = System.Drawing.SystemColors.Window;
            this.l_Gaps.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_Gaps.Location = new System.Drawing.Point(10, 55);
            this.l_Gaps.Margin = new System.Windows.Forms.Padding(3);
            this.l_Gaps.Name = "l_Gaps";
            this.l_Gaps.Size = new System.Drawing.Size(48, 20);
            this.l_Gaps.TabIndex = 86;
            this.l_Gaps.Tag = "";
            this.l_Gaps.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_Gaps, "The number of steps ignored as a result of the track gap checking.");
            // 
            // l_Coalesed
            // 
            this.l_Coalesed.BackColor = System.Drawing.SystemColors.Window;
            this.l_Coalesed.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.l_Coalesed.Location = new System.Drawing.Point(64, 55);
            this.l_Coalesed.Margin = new System.Windows.Forms.Padding(3);
            this.l_Coalesed.Name = "l_Coalesed";
            this.l_Coalesed.Size = new System.Drawing.Size(48, 20);
            this.l_Coalesed.TabIndex = 89;
            this.l_Coalesed.Tag = "";
            this.l_Coalesed.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.tt_Help.SetToolTip(this.l_Coalesed, "The number of move steps coalesed prior to performing the analysis.\nSteps are coa" +
                    "lesced if they form part of a continuous movement in one direction.");
            // 
            // groupBox17
            // 
            this.groupBox17.BackColor = System.Drawing.Color.Transparent;
            this.groupBox17.Controls.Add(this.groupBox4);
            this.groupBox17.Controls.Add(this.groupBox3);
            this.groupBox17.Controls.Add(this.pb_Progress);
            this.groupBox17.Controls.Add(this.groupBox2);
            this.groupBox17.Controls.Add(this.b_MLE_Quick);
            this.groupBox17.Controls.Add(this.b_MLE);
            this.groupBox17.Location = new System.Drawing.Point(12, 107);
            this.groupBox17.Name = "groupBox17";
            this.groupBox17.Size = new System.Drawing.Size(697, 252);
            this.groupBox17.TabIndex = 0;
            this.groupBox17.TabStop = false;
            this.groupBox17.Text = "Maximum Likelihood Estimation";
            // 
            // label58
            // 
            this.label58.AutoSize = true;
            this.label58.Location = new System.Drawing.Point(195, 23);
            this.label58.Name = "label58";
            this.label58.Size = new System.Drawing.Size(35, 13);
            this.label58.TabIndex = 67;
            this.label58.Text = "Fitting";
            // 
            // groupBox4
            // 
            this.groupBox4.Controls.Add(this.cb_MLE_Fitting);
            this.groupBox4.Controls.Add(this.label58);
            this.groupBox4.Controls.Add(this.tb_MaxGap);
            this.groupBox4.Controls.Add(this.cb_Coalesce);
            this.groupBox4.Controls.Add(this.label6);
            this.groupBox4.Controls.Add(this.cb_MLE_Discrete);
            this.groupBox4.Controls.Add(this.cb_MLE_ptest);
            this.groupBox4.Location = new System.Drawing.Point(6, 78);
            this.groupBox4.Name = "groupBox4";
            this.groupBox4.Size = new System.Drawing.Size(550, 53);
            this.groupBox4.TabIndex = 0;
            this.groupBox4.TabStop = false;
            this.groupBox4.Text = "Parameters";
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(6, 23);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(125, 13);
            this.label6.TabIndex = 70;
            this.label6.Text = "Maximum gap (hh:mm:ss)";
            // 
            // groupBox3
            // 
            this.groupBox3.Controls.Add(this.label1);
            this.groupBox3.Controls.Add(this.cb_Dimension);
            this.groupBox3.Controls.Add(this.cb_MLE_AltDist);
            this.groupBox3.Controls.Add(this.cb_MLE_Dist);
            this.groupBox3.Controls.Add(this.label48);
            this.groupBox3.Controls.Add(this.label54);
            this.groupBox3.Location = new System.Drawing.Point(6, 19);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(550, 53);
            this.groupBox3.TabIndex = 72;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Distributions";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(408, 22);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(56, 13);
            this.label1.TabIndex = 63;
            this.label1.Text = "Dimension";
            // 
            // label48
            // 
            this.label48.AutoSize = true;
            this.label48.Location = new System.Drawing.Point(6, 22);
            this.label48.Name = "label48";
            this.label48.Size = new System.Drawing.Size(59, 13);
            this.label48.TabIndex = 60;
            this.label48.Text = "Distribution";
            // 
            // label54
            // 
            this.label54.AutoSize = true;
            this.label54.Location = new System.Drawing.Point(212, 22);
            this.label54.Name = "label54";
            this.label54.Size = new System.Drawing.Size(49, 13);
            this.label54.TabIndex = 61;
            this.label54.Text = "Alternate";
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.l_Coalesed);
            this.groupBox2.Controls.Add(this.label4);
            this.groupBox2.Controls.Add(this.label2);
            this.groupBox2.Controls.Add(this.l_Gaps);
            this.groupBox2.Controls.Add(this.l_MLE_AltAICw);
            this.groupBox2.Controls.Add(this.l_MLE_AICw);
            this.groupBox2.Controls.Add(this.l_MLE_AltGOF);
            this.groupBox2.Controls.Add(this.l_MLE_p);
            this.groupBox2.Controls.Add(this.l_MLE_Xmax);
            this.groupBox2.Controls.Add(this.l_MLE_GOF);
            this.groupBox2.Controls.Add(this.l_MLE_Xmin);
            this.groupBox2.Controls.Add(this.label63);
            this.groupBox2.Controls.Add(this.l_MLE_Exponent);
            this.groupBox2.Controls.Add(this.label61);
            this.groupBox2.Controls.Add(this.label60);
            this.groupBox2.Controls.Add(this.label46);
            this.groupBox2.Controls.Add(this.label62);
            this.groupBox2.Controls.Add(this.label59);
            this.groupBox2.Controls.Add(this.l_xmin);
            this.groupBox2.Controls.Add(this.l_exp);
            this.groupBox2.Location = new System.Drawing.Point(6, 137);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(682, 89);
            this.groupBox2.TabIndex = 71;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Results";
            // 
            // label4
            // 
            this.label4.Location = new System.Drawing.Point(61, 17);
            this.label4.Name = "label4";
            this.label4.Padding = new System.Windows.Forms.Padding(3);
            this.label4.Size = new System.Drawing.Size(62, 35);
            this.label4.TabIndex = 88;
            this.label4.Text = "Steps coalesed";
            this.label4.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label2
            // 
            this.label2.Location = new System.Drawing.Point(8, 17);
            this.label2.Name = "label2";
            this.label2.Padding = new System.Windows.Forms.Padding(3);
            this.label2.Size = new System.Drawing.Size(50, 35);
            this.label2.TabIndex = 87;
            this.label2.Text = "Gaps ignored";
            this.label2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label63
            // 
            this.label63.Location = new System.Drawing.Point(627, 36);
            this.label63.Name = "label63";
            this.label63.Size = new System.Drawing.Size(48, 16);
            this.label63.TabIndex = 66;
            this.label63.Text = "p value";
            this.label63.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label61
            // 
            this.label61.Location = new System.Drawing.Point(569, 36);
            this.label61.Name = "label61";
            this.label61.Size = new System.Drawing.Size(48, 16);
            this.label61.TabIndex = 60;
            this.label61.Text = "Alt AICw";
            this.label61.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label60
            // 
            this.label60.Location = new System.Drawing.Point(515, 36);
            this.label60.Name = "label60";
            this.label60.Size = new System.Drawing.Size(48, 16);
            this.label60.TabIndex = 62;
            this.label60.Text = "AICw";
            this.label60.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label46
            // 
            this.label46.Location = new System.Drawing.Point(451, 36);
            this.label46.Name = "label46";
            this.label46.Size = new System.Drawing.Size(48, 16);
            this.label46.TabIndex = 64;
            this.label46.Text = "Alt GOF";
            this.label46.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label62
            // 
            this.label62.Location = new System.Drawing.Point(292, 34);
            this.label62.Name = "label62";
            this.label62.Size = new System.Drawing.Size(80, 20);
            this.label62.TabIndex = 67;
            this.label62.Text = "Xmax";
            this.label62.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label59
            // 
            this.label59.Location = new System.Drawing.Point(397, 36);
            this.label59.Name = "label59";
            this.label59.Size = new System.Drawing.Size(48, 16);
            this.label59.TabIndex = 68;
            this.label59.Text = "GOF (D)";
            this.label59.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // l_xmin
            // 
            this.l_xmin.Location = new System.Drawing.Point(206, 36);
            this.l_xmin.Name = "l_xmin";
            this.l_xmin.Size = new System.Drawing.Size(80, 20);
            this.l_xmin.TabIndex = 69;
            this.l_xmin.Text = "Xmin";
            this.l_xmin.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // l_exp
            // 
            this.l_exp.Location = new System.Drawing.Point(133, 36);
            this.l_exp.Name = "l_exp";
            this.l_exp.Size = new System.Drawing.Size(67, 16);
            this.l_exp.TabIndex = 70;
            this.l_exp.Text = "Exponent";
            this.l_exp.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.importFileToolStripMenuItem,
            this.helpToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(721, 24);
            this.menuStrip1.TabIndex = 5;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // importFileToolStripMenuItem
            // 
            this.importFileToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.m_ImportFile});
            this.importFileToolStripMenuItem.Name = "importFileToolStripMenuItem";
            this.importFileToolStripMenuItem.Size = new System.Drawing.Size(37, 20);
            this.importFileToolStripMenuItem.Text = "File";
            // 
            // m_ImportFile
            // 
            this.m_ImportFile.Image = ((System.Drawing.Image)(resources.GetObject("m_ImportFile.Image")));
            this.m_ImportFile.Name = "m_ImportFile";
            this.m_ImportFile.Size = new System.Drawing.Size(129, 22);
            this.m_ImportFile.Text = "Import file";
            this.m_ImportFile.Click += new System.EventHandler(this.m_ImportFile_Click);
            // 
            // helpToolStripMenuItem
            // 
            this.helpToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.enableToolTipsToolStripMenuItem,
            this.aboutToolStripMenuItem});
            this.helpToolStripMenuItem.Name = "helpToolStripMenuItem";
            this.helpToolStripMenuItem.Size = new System.Drawing.Size(44, 20);
            this.helpToolStripMenuItem.Text = "Help";
            // 
            // enableToolTipsToolStripMenuItem
            // 
            this.enableToolTipsToolStripMenuItem.CheckOnClick = true;
            this.enableToolTipsToolStripMenuItem.Image = ((System.Drawing.Image)(resources.GetObject("enableToolTipsToolStripMenuItem.Image")));
            this.enableToolTipsToolStripMenuItem.Name = "enableToolTipsToolStripMenuItem";
            this.enableToolTipsToolStripMenuItem.Size = new System.Drawing.Size(157, 22);
            this.enableToolTipsToolStripMenuItem.Text = "Enable help tips";
            this.enableToolTipsToolStripMenuItem.Click += new System.EventHandler(this.enableToolTipsToolStripMenuItem_Click);
            // 
            // aboutToolStripMenuItem
            // 
            this.aboutToolStripMenuItem.Image = ((System.Drawing.Image)(resources.GetObject("aboutToolStripMenuItem.Image")));
            this.aboutToolStripMenuItem.Name = "aboutToolStripMenuItem";
            this.aboutToolStripMenuItem.Size = new System.Drawing.Size(157, 22);
            this.aboutToolStripMenuItem.Text = "About";
            this.aboutToolStripMenuItem.Click += new System.EventHandler(this.aboutToolStripMenuItem_Click);
            // 
            // tt_Help
            // 
            this.tt_Help.Active = false;
            this.tt_Help.AutomaticDelay = 50;
            this.tt_Help.AutoPopDelay = 60000;
            this.tt_Help.InitialDelay = 10;
            this.tt_Help.IsBalloon = true;
            this.tt_Help.ReshowDelay = 10;
            // 
            // Form1
            // 
            this.AllowDrop = true;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(721, 382);
            this.Controls.Add(this.l_Status);
            this.Controls.Add(this.groupBox17);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.menuStrip1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MainMenuStrip = this.menuStrip1;
            this.MaximizeBox = false;
            this.Name = "Form1";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "MBA MLE Analysis";
            this.DragDrop += new System.Windows.Forms.DragEventHandler(this.panel1_DragDrop);
            this.DragEnter += new System.Windows.Forms.DragEventHandler(this.panel1_DragEnter);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.groupBox17.ResumeLayout(false);
            this.groupBox4.ResumeLayout(false);
            this.groupBox4.PerformLayout();
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.OpenFileDialog OFD1;
		private System.Windows.Forms.GroupBox groupBox1;
		private System.Windows.Forms.Label l1;
		internal System.Windows.Forms.GroupBox groupBox17;
		private System.Windows.Forms.Label label58;
        private System.Windows.Forms.ComboBox cb_MLE_Fitting;
		private System.Windows.Forms.Label label54;
		private System.Windows.Forms.Label label48;
		internal System.Windows.Forms.ComboBox cb_MLE_AltDist;
		internal System.Windows.Forms.CheckBox cb_MLE_ptest;
		internal System.Windows.Forms.ComboBox cb_MLE_Dist;
		internal System.Windows.Forms.CheckBox cb_MLE_Discrete;
		internal System.Windows.Forms.Button b_MLE_Quick;
		internal System.Windows.Forms.Button b_MLE;
		public System.Windows.Forms.Label l2;
		public System.Windows.Forms.ProgressBar pb_Progress;
		private System.Windows.Forms.Label label6;
		private System.Windows.Forms.TextBox tb_MaxGap;
		private System.Windows.Forms.CheckBox cb_Coalesce;
		private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.GroupBox groupBox2;
		internal System.Windows.Forms.Label l_MLE_AltAICw;
		internal System.Windows.Forms.Label l_MLE_AICw;
		internal System.Windows.Forms.Label l_MLE_AltGOF;
		internal System.Windows.Forms.Label l_MLE_p;
		internal System.Windows.Forms.Label l_MLE_Xmax;
		internal System.Windows.Forms.Label l_MLE_GOF;
		internal System.Windows.Forms.Label l_MLE_Xmin;
		internal System.Windows.Forms.Label l_MLE_Exponent;
        internal System.Windows.Forms.Label label61;
        internal System.Windows.Forms.Label label60;
        internal System.Windows.Forms.Label label46;
		internal System.Windows.Forms.Label label63;
		internal System.Windows.Forms.Label label62;
		internal System.Windows.Forms.Label label59;
		internal System.Windows.Forms.Label l_xmin;
        internal System.Windows.Forms.Label l_exp;
		private System.Windows.Forms.GroupBox groupBox4;
		public System.Windows.Forms.Label l3;
		public System.Windows.Forms.Label l_Status;
		private System.Windows.Forms.MenuStrip menuStrip1;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.ComboBox cb_Dimension;
		private System.Windows.Forms.ToolStripMenuItem importFileToolStripMenuItem;
		private System.Windows.Forms.ToolStripMenuItem m_ImportFile;
		internal System.Windows.Forms.Label l_Gaps;
		internal System.Windows.Forms.Label l_Coalesed;
		internal System.Windows.Forms.Label label4;
		internal System.Windows.Forms.Label label2;
		public System.Windows.Forms.Label label8;
		public System.Windows.Forms.Label label7;
		public System.Windows.Forms.Label label5;
		private System.Windows.Forms.Label l_Filename;
		private System.Windows.Forms.Label l_MaxGap;
		private System.Windows.Forms.Label l_MinGap;
		private System.Windows.Forms.Label l_MaxStep;
		private System.Windows.Forms.Label l_MinStep;
		public System.Windows.Forms.Label l_Points;
		private System.Windows.Forms.ToolTip tt_Help;
		private System.Windows.Forms.ToolStripMenuItem helpToolStripMenuItem;
		private System.Windows.Forms.ToolStripMenuItem enableToolTipsToolStripMenuItem;
		private System.Windows.Forms.ToolStripMenuItem aboutToolStripMenuItem;
	}
}

