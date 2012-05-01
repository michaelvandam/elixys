package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Reagents extends JSONObject
	{
		// Constructor
		public function Reagents(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
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
			return "reagents";
		}

		// Data wrappers
		public function get ReagentList():Array
		{
			// Parse the reagents
			if (m_pReagents == null)
			{
				m_pReagents = new Array();
				var pReagents:Array = super.flash_proxy::getProperty("reagents");
				for each (var pReagentObject:Object in pReagents)
				{
					var pReagent:Reagent = new Reagent(null, pReagentObject);
					m_pReagents.push(pReagent);
				}
			}
			return m_pReagents;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"reagents\"," +
			"\"reagents\":{}}";

		// State components
		private var m_pReagents:Array;
	}
}
