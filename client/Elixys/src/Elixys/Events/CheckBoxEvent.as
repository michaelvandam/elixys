package Elixys.Events
{
	import Elixys.Components.CheckBox;
	
	import flash.events.Event;

	// This custom event is used to relay check box messages
	public class CheckBoxEvent extends Event
	{
		// Constructor
		public function CheckBoxEvent(pCheckBox:CheckBox, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			checkbox = pCheckBox;
			super(CHANGE, bubbles, cancelable);
		}

		// Event name
		static public var CHANGE:String = "CheckBoxChange";
		
		// Check box references
		public var checkbox:CheckBox;
	}
}
