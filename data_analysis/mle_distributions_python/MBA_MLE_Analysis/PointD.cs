
namespace MBA_MLE_Analysis
{
	public class PointD
	{
		public double X, Y;

		public PointD(double x, double y)
		{
			X = x;
			Y = y;
		}

        public PointD(PointD p)
        {
            X = p.X;
            Y = p.Y;
        }

		public PointD()
		{
			X = 0;
			Y = 0;
		}

        public bool isEmpty() { return X == 0.0 && Y == 0.0; }
	}
}
