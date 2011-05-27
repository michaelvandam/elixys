package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class StatePrompt extends State
	{
		// Constructor
		public function StatePrompt(data:String, existingcontent:Object = null)
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
			return (sState.substring(0, TYPE.length) == TYPE);
		}

		// Data wrappers
		public function Text1():String
		{
			return super.flash_proxy::getProperty("text1");
		}
		public function Edit1():Boolean
		{
			return (super.flash_proxy::getProperty("edit1") == "true");
		}
		public function Text2():String
		{
			return super.flash_proxy::getProperty("text2");
		}
		public function Edit2():Boolean
		{
			return (super.flash_proxy::getProperty("edit2") == "true");
		}
		public function Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("buttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		
		// Type
		static public var TYPE:String = "PROMPT";
		
		// State components
		private var m_pButtons:Array;
	}
}
