package Elixys.Views
{
	import com.danielfreeman.madcomponents.*;

	import Elixys.Assets.Styling;
	import Elixys.Components.Screen;
	
	import flash.display.Sprite;
	
	// This select view is an extension of the Screen class
	public class Select extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function Select(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			super(screen, SELECT, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 3;
		
		// Loads the next child component and return true or returns false if the load is complete
		protected var m_nChildrenLoaded:uint = 0;
		public override function LoadNext():Boolean
		{
			if (m_nChildrenLoaded < LOAD_STEPS)
			{
				++m_nChildrenLoaded;
				return true;
			}
			else
			{
				return false;
			}
		}

		/***
		 * Member variables
		 **/

		// Select screen XML
		protected static const SELECT:XML =
			<frame background="#FF00FF">
				<label>
					<font color={Styling.TEXT_GRAY} size="40">
						Select page
					</font>
				</label>
			</frame>;
	}
}
