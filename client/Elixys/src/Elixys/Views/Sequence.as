package Elixys.Views
{
	import Elixys.Components.Screen;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	
	// This sequence view is an extension of the screen class
	public class Sequence extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function Sequence(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			super(screen, pElixys, SEQUENCE, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 19;
		
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

		// Sequence view XML
		protected static const SEQUENCE:XML = <frame background="#00FFFF" />;
	}
}

