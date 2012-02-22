package
{
	import com.christiancantrell.nativetext.NativeText;
	
	import flash.display.Sprite;

	// Set the application size to match the iPad2
	[SWF(width="1024", height="768")]
	
	// This is the root of the Elixys application
	public class ElixysAIR extends Elixys
	{
		/***
		 * Construction
		 **/
		
		public function ElixysAIR(screen:Sprite = null)
		{
			// Call the base constructor
			super(screen);
		}
		
		/***
		 * Member variables
		 **/
		
		// Unused reference to NativeText so it will be compiled into the project
		private static var m_pNativeText:NativeText;
	}
}

