package Elixys.Components
{
	import Elixys.Extended.Form;
	import Elixys.JSON.State.State;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	
	// This screen component is an extension of the Form class
	public class Screen extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Screen(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, xml, attributes, row, inGroup);
		}
		
		/***
		 * Member functions
		 **/
		
		// Loads the next child component.  Return true if loading or false if the load is complete
		public function LoadNext():Boolean
		{
			return false;
		}
		
		// Updates the state
		public function UpdateState(pState:State):void
		{
		}
	}
}
