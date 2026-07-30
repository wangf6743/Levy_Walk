// This class has methods to create and verify the MBA software licenses
using System;
using System.IO;
using System.Reflection;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Security.Cryptography;
using System.Windows.Forms;

namespace MBA_Licence
{
	class MBA_Licence
	{
		// The encryption keys
		private static byte[] desKey = { 15, 54, 12, 54, 89, 65, 32, 88 };
		private static byte[] desIV = { 17, 19, 27, 55, 123, 158, 169, 203 };

		public	const int	DiveAnalysis = 0,
							TrackAnalysis = 1,
							ForagingLab = 2,
							PredatorPrey = 3,
							GridOccupancy = 4,
							MLE_Analysis = 5;

        private const string LicenceName = "MBA_MLE.lic";

		// The license fields
		public static bool	OK = false;

		// Perform license validation
		//	This method will be used by the calling program to check a valid license exists
		public static void CheckLicence(int p_ProductCode)
		{
			SaveLicense MyLicense = null;
			DateTime	MBA_ExpiryDate = new DateTime(1000, 10, 28);
			string		LicenseFile;
			int			DaysRemaining;
			bool		Invalid = false,
						Expired = false;

			OK = false;

			// If the program is running at the MBA then we check the all software license
			try
			{
				if (File.Exists(@"R:\Sims Archive Store\Software\MBA_Licences\" + LicenceName))
				{
					MyLicense = Read(@"R:\Sims Archive Store\Software\MBA_Licences\" + LicenceName);

					// Verify the license
					if (MyLicense == null) Invalid = true;
					else
					{
						if (!MyLicense.CheckHash()) Invalid = true;
						if (!MyLicense.Products[p_ProductCode]) Invalid = true;
						if (!MyLicense.UserName.Equals("All MBA users")) Invalid = true;
						if (!MyLicense.MachineName.Equals("ALL MBA MACHINES")) Invalid = true;
						if (MyLicense.ExpiryDate.CompareTo(MBA_ExpiryDate) != 0) Expired = true;
					}
				}

				else
				{
					// Check for a specific license file
					LicenseFile = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments) + "\\" + LicenceName;

					if (File.Exists(LicenseFile)) MyLicense = Read(LicenseFile);

					// Verify the license
					if (MyLicense == null) Invalid = true;
					else
					{
						if (!MyLicense.CheckHash()) Invalid = true;
						if (!MyLicense.Products[p_ProductCode]) Invalid = true;
						if (!MyLicense.UserName.Equals(Environment.UserName)) Invalid = true;
						if (MyLicense.MachineName != string.Empty && !MyLicense.MachineName.Equals(Environment.MachineName.ToUpperInvariant())) Invalid = true;
						if (MyLicense.ExpiryDate.CompareTo(DateTime.Now) <= 0) Expired = true;
					}
				}
			}
			catch (Exception)
			{
				Invalid = true;
			}

            // Report problems
            if (Invalid)
            {
                MessageBox.Show("No valid license found", "MBA Software licensing error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            if (Expired)
            {
                MessageBox.Show("License is expired", "MBA Software licensing error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            DaysRemaining = (int)MyLicense.ExpiryDate.Subtract(DateTime.Now).TotalDays;

            if (DaysRemaining < 31 && DaysRemaining > 0)
            {
                MessageBox.Show("Licence will expire in " + DaysRemaining.ToString() + " days", "MBA Software licensing", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }

			OK = true;
		}
	
		// Verify a specific license file
		public static void VerifyLicense(string p_FileName, bool[] p_Products, string p_UserName, string p_MachineName)
		{
			SaveLicense MyLicense = null;
			int			DaysRemaining;
			bool		Invalid = false, 
						Expired = false;

			// Read the file
			MyLicense = Read(p_FileName);

			// Verify the license
			try
			{
				if (MyLicense == null) Invalid = true;
				else
				{
					if (!MyLicense.CheckHash()) Invalid = true;
					if (!MyLicense.UserName.Equals(p_UserName)) Invalid = true;
					if (MyLicense.MachineName != string.Empty && !MyLicense.MachineName.Equals(p_MachineName)) Invalid = true;
					if (MyLicense.ExpiryDate.CompareTo(DateTime.Now) <= 0) Expired = true;

					// Check all the product codes
					for (int i = 0; i < p_Products.Length; i++)
					{
						if (p_Products[i] != MyLicense.Products[i]) Invalid = true;
					}

				}
			}
			catch (Exception)
			{
				Invalid = true;
			}

			// Report problems
			if (Invalid)
			{
				MessageBox.Show("No valid licence found", "MBA Software licensing error");
				return;
			}

			if (Expired)
			{
				MessageBox.Show("Licence is expired", "MBA Software licensing error");
				return;
			}

			DaysRemaining = (int)MyLicense.ExpiryDate.Subtract(DateTime.Now).TotalDays;

			if (DaysRemaining < 31 && DaysRemaining > 0)
			{
				MessageBox.Show("Licence will expire in " + DaysRemaining.ToString() + " days", "MBA Software licensing");
				return;
			}

			MessageBox.Show("Licence is valid", "MBA Software licensing");
		}

		// Save a new license
		public static void Save(string p_FileName, bool[] p_Products, string p_UserName, string p_MachineName, DateTime p_ExpiryDate)
		{
			// Serialise to a memory stream 
			SaveLicense MyLicense = new SaveLicense(p_Products, p_UserName, p_MachineName, p_ExpiryDate);
			MemoryStream MyStream = new MemoryStream();
			IFormatter MyFormatter = new BinaryFormatter();
			MyFormatter.Serialize(MyStream, MyLicense);
			MyStream.Close();
			byte[] License =  MyStream.ToArray();

			// Create the file stream
			FileStream fout = new FileStream(p_FileName, FileMode.OpenOrCreate, FileAccess.Write);
			fout.SetLength(License.Length);

			// Create the encrypter
			DES des = new DESCryptoServiceProvider();
			CryptoStream encStream = new CryptoStream(fout, des.CreateEncryptor(desKey, desIV), CryptoStreamMode.Write);

			// Encrypt the license to the output file
			encStream.Write(License, 0, License.Length);
			encStream.Close();
			fout.Close();
		}

		// Read a license
		public static SaveLicense Read(string p_FileName)
		{
			SaveLicense SavedLicense = null;

			try
			{
				// Create the file stream to handle the input
				FileStream InputFileStream = new FileStream(p_FileName, FileMode.Open, FileAccess.Read);

				// Perform the decryption
				DES des = new DESCryptoServiceProvider();
				CryptoStream cStream = new CryptoStream(InputFileStream, des.CreateDecryptor(desKey, desIV), CryptoStreamMode.Read);

				// Attempt to deserialise the licence
				IFormatter MyFormatter = new BinaryFormatter();
				MyFormatter.Binder = new MyDeserializationBinder();

				try { SavedLicense = (SaveLicense)MyFormatter.Deserialize(cStream); }
				catch(Exception) {}

				cStream.Close();

			}
			catch (Exception) {}

			return SavedLicense;
		}

		// http://spazzarama.wordpress.com/2009/06/25/binary-deserialize-unable-to-find-assembly/
		//	Note quite sure how this works, but it does
		sealed class MyDeserializationBinder : SerializationBinder
		{
			public override Type BindToType(string assemblyName, string typeName)
			{
				Type typeToDeserialize = null;
		 
				String currentAssembly = Assembly.GetExecutingAssembly().FullName;
		 
				// In this case we are always using the current assembly
				assemblyName = currentAssembly;
		 
				// Get the type using the typeName and assemblyName
				typeToDeserialize = Type.GetType(String.Format("{0}, {1}", typeName, assemblyName));
		 
				return typeToDeserialize;
			}
		}


		// This inner class represents the actual license
		[Serializable]
		public class SaveLicense
		{
			public  bool[]		Products;
			public	string		UserName,
								MachineName;
			public	DateTime	ExpiryDate;
			private short		CheckSum = 0;	// A checksum

			public SaveLicense(bool[] p_Products, string p_UserName, string p_MachineName, DateTime p_ExpiryDate)
			{
				Products = p_Products;
				UserName = p_UserName;
				ExpiryDate = p_ExpiryDate;
				MachineName = p_MachineName;

				// Build the checksum
				CheckSum = getHash();
			}

			// Check the hash key computes correctly
			public bool CheckHash()
			{
				return CheckSum == getHash();
			}

			private short getHash()
			{
				short hash = 0;

				// Build the checksum
				hash += getHash(Products.ToString());
				hash += getHash(UserName);
				hash += getHash(MachineName);
				hash += (short)(ExpiryDate.Ticks / TimeSpan.TicksPerDay);

				return hash;
			}

			// Compute a simple hash key from strings
			private short getHash(string p)
			{
				if (p == null) return 345;

				short Hash = 0;

				for (int i = 0; i < p.Length; i++)
				{
					Hash += Convert.ToInt16(p[i]);
				}

				return Hash;
			}
		}
	}
}
