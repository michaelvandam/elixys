package Elixys.Views
{
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	
	// This select view is an extension of our extended Form class
	public class Select extends Form
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

		// Select view XML
		protected static const SELECT:XML = <frame background="#00FFFF" />;
	}
}
