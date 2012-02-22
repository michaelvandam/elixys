package Elixys.JSON.State
{
	import flash.utils.flash_proxy;
	
	public class StateSelect extends State
	{
		// Constructor
		public function StateSelect(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ClientState != null) && !CheckState(ClientState.Screen))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "SELECT";
		}

		// Checks for a state match
		static public function CheckState(sState:String):Boolean
		{
			return (sState.substr(0, TYPE.length) == TYPE);
		}

		// Data wrappers
		public function get Tabs():Array
		{
			// Parse the tabs
			if (m_pTabs == null)
			{
				m_pTabs = new Array();
				var pTabs:Array = super.flash_proxy::getProperty("tabs");
				for each (var pTabObject:Object in pTabs)
				{
					var pTab:Tab = new Tab(null, pTabObject);
					m_pTabs.push(pTab);
				}
			}
			return m_pTabs;
		}
		public function get TabID():String
		{
			return super.flash_proxy::getProperty("tabid");
		}
		public function get OptionButtons():Array
		{
			// Parse the buttons
			if (m_pOptionButtons == null)
			{
				m_pOptionButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("optionbuttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pOptionButtons.push(pButton);
				}
			}
			return m_pOptionButtons;
		}
		public function get Sequences():Array
		{
			// Parse the sequences
			if (m_pSequences == null)
			{
				m_pSequences = new Array();
				var pSequences:Array = super.flash_proxy::getProperty("sequences");
				for each (var pSequenceObject:Object in pSequences)
				{
					var pSequence:SequenceMetadata = new SequenceMetadata(null, pSequenceObject);
					m_pSequences.push(pSequence);
				}
			}
			return m_pSequences;
		}
		
		// State components
		private var m_pTabs:Array;
		private var m_pOptionButtons:Array;
		private var m_pSequences:Array;
	}
}
