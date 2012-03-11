package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used to relay item selection messages
	public class SelectionEvent extends Event
	{
		// Constructor
		public function SelectionEvent(sSelectionID:int, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			selectionID = sSelectionID;
			super(CHANGE, bubbles, cancelable);
		}

		// Event name
		static public var CHANGE:String = "SelectionChange";
		
		// Selection ID
		public var selectionID:int = 0;
	}
}
