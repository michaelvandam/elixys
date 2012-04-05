package Elixys.JSON.Configuration
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Configuration extends JSONObject
	{
		// Constructor
		public function Configuration(data:String, existingcontent:Object = null)
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
			return "configuration";
		}
		
		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function get Version():String
		{
			return super.flash_proxy::getProperty("version");
		}
		public function get Debug():Boolean
		{
			var sDebug:String = super.flash_proxy::getProperty("version");
			return (sDebug == "true");
		}
		public function get SupportedOperations():Array
		{
			return super.flash_proxy::getProperty("supportedoperations");
		}
		public function get Reactors():uint
		{
			return super.flash_proxy::getProperty("reactors");
		}
		public function get ReagentsPerReactor():uint
		{
			return super.flash_proxy::getProperty("reagentsperreactor");
		}
		public function get ColumnsPerReactor():uint
		{
			return super.flash_proxy::getProperty("columnsperreactor");
		}
		public function get DisallowedReagentPositions():Array
		{
			// Parse the disallowed reagent positions
			if (m_pDisallowedReagentPositions == null)
			{
				m_pDisallowedReagentPositions = new Array();
				var pDisallowedReagentPositions:Array = super.flash_proxy::getProperty("disallowedreagentpositions");
				for each (var pDisallowedReagentPositionObject:Object in pDisallowedReagentPositions)
				{
					var pDisallowedReagentPosition:DisallowedReagentPosition = 
						new DisallowedReagentPosition(null, pDisallowedReagentPositionObject);
					m_pDisallowedReagentPositions.push(pDisallowedReagentPosition);
				}
			}
			return m_pDisallowedReagentPositions;
		}
		
		// State components
		protected var m_pDisallowedReagentPositions:Array;
	}
}