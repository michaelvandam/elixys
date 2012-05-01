package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used to relay dropdown messages
	public class DropdownEvent extends Event
	{
		// Constructor
		public function DropdownEvent(type:String, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
		}

		// Copy
		public function Copy():DropdownEvent
		{
			var pEvent:DropdownEvent = new DropdownEvent(type);
			pEvent.selectedValue = selectedValue;
			pEvent.selectedData = selectedData;
			return pEvent;
		}
		
		// Event name
		static public var ITEMSELECTED:String = "DropdownItemSelected";
		static public var LISTHIDDEN:String = "DropdownListHidden";
		
		// Button name
		public var selectedValue:String;
		public var selectedData:*;
	}
}
