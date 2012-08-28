package
{
	import Elixys.Assets.Constants;
	
	import com.christiancantrell.nativetext.NativeText;
	
	import flash.display.Sprite;
	import flash.display.StageAlign;
	import flash.display.StageQuality;
	import flash.display.StageScaleMode;
	
	// iPhone
	[SWF(width="320",height="480")]

	public class ElixysiPhone extends Elixys
	{
		/***
		 * Construction
		 **/

		public function ElixysiPhone(screen:Sprite = null)
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