package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class Reagents extends JSONObject
	{
		// Constructor
		public function Reagents(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function get Type():String
		{
			return super.flash_proxy::getProperty("type");
		}

		public function ReagentArray():Array
		{
			// Parse the buttons
			if (m_pReagents == null)
			{
				m_pReagents = new Array();
				var pReagents:Array = super.flash_proxy::getProperty("reagents");
				for each (var pReagentObject:Object in pReagents)
				{
					// Add the reagent
					var pReagent:Reagent = new Reagent(null, pReagentObject);
					m_pReagents.push(pReagent);
				}
			}
			return m_pReagents;
		}

		// Type
		static public var TYPE:String = "reagents";

		// State components
		private var m_pReagents:Array;
	}
}
