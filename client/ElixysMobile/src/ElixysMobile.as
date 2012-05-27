package
{
	import com.christiancantrell.nativetext.NativeText;
	
	import flash.display.Sprite;
	import flash.display.StageAlign;
	import flash.display.StageQuality;
	import flash.display.StageScaleMode;
	
	// Set the application size to match the iPad 2 or 3
	[SWF(width="1024", height="768")]
	//[SWF(width="2048", height="1536")]

	public class ElixysMobile extends Elixys
	{
		/***
		 * Construction
		 **/

		public function ElixysMobile(screen:Sprite = null)
		{
			// Call the base constructor
			super(screen);
		}

		/***
		 * Member variables
		 **/
		
		// Unused reference to NativeText so it will be compiled into the project
		protected static var m_pNativeText:NativeText;
	}
}