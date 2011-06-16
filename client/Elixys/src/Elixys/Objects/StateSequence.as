package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class StateSequence extends State
	{
		// Constructor
		public function StateSequence(sType:String, data:String, existingcontent:Object = null)
		{
			// Remember our type
			m_sType = sType;
			
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ClientState() != null) && !CheckState(m_sType, ClientState()))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Checks for a state match
		static public function CheckState(sType:String, sState:String):Boolean
		{
			return (sState.substr(0, sType.length) == sType);
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
		public function SequenceID():uint
		{
			return parseInt(super.flash_proxy::getProperty("sequenceid"));
		}
		public function ComponentID():uint
		{
			return parseInt(super.flash_proxy::getProperty("componentid"));
		}
		
		// Types
		static public var VIEWTYPE:String = "VIEW";
		static public var EDITTYPE:String = "EDIT";
		static public var RUNSEQUENCETYPE:String = "RUNSEQUENCE";
		static public var MANUALRUNTYPE:String = "MANUALRUN";
		
		// State components
		protected var m_sType:String;
		protected var m_pButtons:Array;
	}
}
