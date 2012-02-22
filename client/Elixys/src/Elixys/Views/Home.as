package Elixys.Views
{
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	
	// This home view is an extension of our extended Form class
	public class Home extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Home(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			super(screen, HOME, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 1;
		
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

		// Home view XML
		protected static const HOME:XML = <frame background="#00FFFF" />;
	}
}
