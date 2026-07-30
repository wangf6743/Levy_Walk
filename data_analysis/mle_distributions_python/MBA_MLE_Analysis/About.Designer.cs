namespace MBA_MLE_Analysis
{
	partial class About
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
			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(About));
			this.l_ProductName = new System.Windows.Forms.Label();
			this.l_Version = new System.Windows.Forms.Label();
			this.l_Copyright = new System.Windows.Forms.Label();
			this.logoPictureBox = new System.Windows.Forms.PictureBox();
			this.ll_WebLink = new System.Windows.Forms.LinkLabel();
			this.b_OK = new System.Windows.Forms.Button();
			this.rtb1 = new System.Windows.Forms.RichTextBox();
			((System.ComponentModel.ISupportInitialize)(this.logoPictureBox)).BeginInit();
			this.SuspendLayout();
			// 
			// l_ProductName
			// 
			this.l_ProductName.AutoEllipsis = true;
			this.l_ProductName.AutoSize = true;
			this.l_ProductName.Location = new System.Drawing.Point(118, 12);
			this.l_ProductName.Margin = new System.Windows.Forms.Padding(3);
			this.l_ProductName.MaximumSize = new System.Drawing.Size(0, 17);
			this.l_ProductName.Name = "l_ProductName";
			this.l_ProductName.Size = new System.Drawing.Size(75, 13);
			this.l_ProductName.TabIndex = 25;
			this.l_ProductName.Text = "Product Name";
			this.l_ProductName.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
			// 
			// l_Version
			// 
			this.l_Version.AutoSize = true;
			this.l_Version.Location = new System.Drawing.Point(118, 31);
			this.l_Version.Margin = new System.Windows.Forms.Padding(3);
			this.l_Version.MaximumSize = new System.Drawing.Size(0, 17);
			this.l_Version.Name = "l_Version";
			this.l_Version.Size = new System.Drawing.Size(42, 13);
			this.l_Version.TabIndex = 24;
			this.l_Version.Text = "Version";
			this.l_Version.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
			// 
			// l_Copyright
			// 
			this.l_Copyright.AutoSize = true;
			this.l_Copyright.Location = new System.Drawing.Point(118, 50);
			this.l_Copyright.Margin = new System.Windows.Forms.Padding(3);
			this.l_Copyright.MaximumSize = new System.Drawing.Size(0, 17);
			this.l_Copyright.Name = "l_Copyright";
			this.l_Copyright.Size = new System.Drawing.Size(51, 13);
			this.l_Copyright.TabIndex = 26;
			this.l_Copyright.Text = "Copyright";
			this.l_Copyright.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
			// 
			// logoPictureBox
			// 
			this.logoPictureBox.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Stretch;
			this.logoPictureBox.Image = ((System.Drawing.Image)(resources.GetObject("logoPictureBox.Image")));
			this.logoPictureBox.Location = new System.Drawing.Point(12, 12);
			this.logoPictureBox.Name = "logoPictureBox";
			this.logoPictureBox.Size = new System.Drawing.Size(100, 100);
			this.logoPictureBox.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
			this.logoPictureBox.TabIndex = 13;
			this.logoPictureBox.TabStop = false;
			// 
			// ll_WebLink
			// 
			this.ll_WebLink.AutoSize = true;
			this.ll_WebLink.Location = new System.Drawing.Point(118, 187);
			this.ll_WebLink.Name = "ll_WebLink";
			this.ll_WebLink.Size = new System.Drawing.Size(63, 13);
			this.ll_WebLink.TabIndex = 27;
			this.ll_WebLink.TabStop = true;
			this.ll_WebLink.Text = "Visit simslab";
			this.ll_WebLink.LinkClicked += new System.Windows.Forms.LinkLabelLinkClickedEventHandler(this.linkLabel1_LinkClicked);
			// 
			// b_OK
			// 
			this.b_OK.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
			this.b_OK.DialogResult = System.Windows.Forms.DialogResult.OK;
			this.b_OK.Location = new System.Drawing.Point(342, 182);
			this.b_OK.Name = "b_OK";
			this.b_OK.Size = new System.Drawing.Size(75, 23);
			this.b_OK.TabIndex = 29;
			this.b_OK.Text = "OK";
			this.b_OK.UseVisualStyleBackColor = true;
			// 
			// rtb1
			// 
			this.rtb1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
						| System.Windows.Forms.AnchorStyles.Left)
						| System.Windows.Forms.AnchorStyles.Right)));
			this.rtb1.BackColor = System.Drawing.SystemColors.Window;
			this.rtb1.BorderStyle = System.Windows.Forms.BorderStyle.None;
			this.rtb1.Location = new System.Drawing.Point(121, 69);
			this.rtb1.Name = "rtb1";
			this.rtb1.ReadOnly = true;
			this.rtb1.Size = new System.Drawing.Size(296, 103);
			this.rtb1.TabIndex = 31;
			this.rtb1.Text = resources.GetString("rtb1.Text");
			// 
			// About
			// 
			this.AcceptButton = this.b_OK;
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.BackColor = System.Drawing.SystemColors.Window;
			this.ClientSize = new System.Drawing.Size(429, 213);
			this.ControlBox = false;
			this.Controls.Add(this.rtb1);
			this.Controls.Add(this.b_OK);
			this.Controls.Add(this.ll_WebLink);
			this.Controls.Add(this.l_ProductName);
			this.Controls.Add(this.l_Version);
			this.Controls.Add(this.l_Copyright);
			this.Controls.Add(this.logoPictureBox);
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Name = "About";
			this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
			this.Text = "About MBA MLE Analysis";
			((System.ComponentModel.ISupportInitialize)(this.logoPictureBox)).EndInit();
			this.ResumeLayout(false);
			this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.Label l_ProductName;
		private System.Windows.Forms.Label l_Version;
		private System.Windows.Forms.Label l_Copyright;
		private System.Windows.Forms.PictureBox logoPictureBox;
		private System.Windows.Forms.LinkLabel ll_WebLink;
        private System.Windows.Forms.Button b_OK;
		private System.Windows.Forms.RichTextBox rtb1;
	}
}