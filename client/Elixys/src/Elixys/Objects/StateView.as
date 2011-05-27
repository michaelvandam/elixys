package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class StateView extends State
	{
		// Constructor
		public function StateView(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ClientState() != null) && !CheckState(ClientState()))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Checks for a state match
		static public function CheckState(sState:String):Boolean
		{
			return (sState.substr(0, TYPE.length) == TYPE);
		}

		// Data wrappers
		public function Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("navigationbuttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		public function SequenceID():String
		{
			return super.flash_proxy::getProperty("sequenceid");
		}
		public function ComponentID():String
		{
			return super.flash_proxy::getProperty("componentid");
		}
		
		// Type
		static public var TYPE:String = "VIEW";
		
		// State components
		private var m_pButtons:Array;
	}
}
