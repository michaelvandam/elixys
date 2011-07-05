package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used by the child views to inform the parent that they have been created and are ready to be used
	public class ChildCreationCompleteEvent extends Event
	{
		// Constructor
		public function ChildCreationCompleteEvent(bSplashScreen:Boolean = false, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			splashScreen = bSplashScreen;
			super(CHILDCREATIONCOMPLETE, bubbles, cancelable);
		}

		// Event name
		static public var CHILDCREATIONCOMPLETE:String = "ChildCreationCompleteEvent";

		// Splash screen flag
		public var splashScreen:Boolean = false;
	}
}
