package Elixys.Events
{
	import flash.events.Event;

	import Elixys.Extended.Form;

	// This is dispatched when a transition is complete
	public class TransitionCompleteEvent extends Event
	{
		// Constructor
		public function TransitionCompleteEvent(pForm:Form, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			m_pForm = pForm;
			super(TRANSITIONCOMPLETE, bubbles, cancelable);
		}

		// Event name
		static public var TRANSITIONCOMPLETE:String = "TransitionCompleteEvent";

		// Source form
		public var m_pForm:Form;
	}
}
