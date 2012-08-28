package
{
	import Elixys.Assets.Constants;
	
	import com.christiancantrell.nativetext.NativeText;
	
	import flash.display.Sprite;
	import flash.display.StageAlign;
	import flash.display.StageQuality;
	import flash.display.StageScaleMode;
	
	// iPad 1 and 2
	[SWF(width="1024",height="768")]
	
	public class ElixysiPad extends Elixys
	{
		/***
		 * Construction
		 **/

		public function ElixysiPad(screen:Sprite = null)
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