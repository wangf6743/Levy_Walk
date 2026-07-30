using System.Reflection;
using System.Windows.Forms;

namespace MBA_MLE_Analysis
{
	public partial class About : Form
	{
		public About()
		{
			InitializeComponent();

			l_ProductName.Text = AssemblyProduct;
			l_Version.Text = "Version " + Writer.Version;
			l_Copyright.Text = AssemblyCopyright;

			// Set up the web link
			ll_WebLink.Links[0].LinkData = "http://www.mba.ac.uk/simslab/";
		}

		#region Assembly Attribute Accessors

		public string AssemblyProduct
		{
			get
			{
				object[] attributes = Assembly.GetExecutingAssembly().GetCustomAttributes(typeof(AssemblyProductAttribute), false);
				if (attributes.Length == 0)
				{
					return "";
				}
				return ((AssemblyProductAttribute)attributes[0]).Product;
			}
		}

		public string AssemblyCopyright
		{
			get
			{
				object[] attributes = Assembly.GetExecutingAssembly().GetCustomAttributes(typeof(AssemblyCopyrightAttribute), false);
				if (attributes.Length == 0)
				{
					return "";
				}
				return ((AssemblyCopyrightAttribute)attributes[0]).Copyright;
			}
		}

		#endregion

		private void linkLabel1_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
		{
			// Determine which link was clicked within the LinkLabel. 
			ll_WebLink.Links[ll_WebLink.Links.IndexOf(e.Link)].Visited = true;

			// Display the appropriate link based on the value of the  
			// LinkData property of the Link object. 
			string target = (string)e.Link.LinkData;

			// If the value looks like a URL, navigate to it. Otherwise, display it in a message box. 
			if (null != target && target.StartsWith("http://www"))
			{
				System.Diagnostics.Process.Start(target);
			}
		}
	}
}
