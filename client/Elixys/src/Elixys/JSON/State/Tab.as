package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Tab extends JSONObject
	{
		// Constructor
		public function Tab(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}

		// Static type
		public static function get TYPE():String
		{
			return "tab";
		}

		// Data wrappers
		public function get Text():String
		{
			return super.flash_proxy::getProperty("text");
		}
		public function get ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
		public function get Columns():Array
		{
			// Parse the columns
			if (m_pColumns == null)
			{
				m_pColumns = new Array();
				var pColumns:Array = super.flash_proxy::getProperty("columns");
				for each (var sColumn:String in pColumns)
				{
					m_pColumns.push(sColumn);
				}
			}
			return m_pColumns;
		}
		
		// State components
		private var m_pColumns:Array;
	}
}
