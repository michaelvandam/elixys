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
		public function get Columns():Array
		{
			// Parse the columns
			if (m_pColumns == null)
			{
				m_pColumns = new Array();
				var pColumns:Array = super.flash_proxy::getProperty("columns");
				for each (var pColumnObject:Object in pColumns)
				{
					var pColumn:Column = new Column(null, pColumnObject);
					m_pColumns.push(pColumn);
				}
			}
			return m_pColumns;
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
		protected var m_pTabs:Array;
		protected var m_pColumns:Array;
		protected var m_pSequences:Array;
	}
}
