package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Reagent extends JSONObject
	{
		// Constructor
		public function Reagent(data:String = null, existingcontent:Object = null)
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
			return "reagent";
		}

		// Copy
		public function Copy(pSourceReagent:Reagent):void
		{
			Available = pSourceReagent.Available;
			ReagentID = pSourceReagent.ReagentID;
			ComponentID = pSourceReagent.ComponentID;
			Position = pSourceReagent.Position;
			Name = pSourceReagent.Name;
			Description = pSourceReagent.Description;
		}
		
		// Data wrappers
		public function get Available():Boolean
		{
			return super.flash_proxy::getProperty("available");
		}
		public function set Available(value:Boolean):void
		{
			super.flash_proxy::setProperty("available", value);
		}

		public function get ReagentID():uint
		{
			return super.flash_proxy::getProperty("reagentid");
		}
		public function set ReagentID(value:uint):void
		{
			super.flash_proxy::setProperty("reagentid", value);
		}

		public function get ComponentID():uint
		{
			return parseInt(super.flash_proxy::getProperty("componentid"));
		}
		public function set ComponentID(value:uint):void
		{
			super.flash_proxy::setProperty("componentid", value);
		}
		
		public function get Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function set Position(value:String):void
		{
			super.flash_proxy::setProperty("position", value);
		}

		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get NameValidation():String
		{
			return super.flash_proxy::getProperty("namevalidation");
		}

		public function get Description():String
		{
			return super.flash_proxy::getProperty("description");
		}
		public function set Description(value:String):void
		{
			super.flash_proxy::setProperty("description", value);
		}

		public function get DescriptionValidation():String
		{
			return super.flash_proxy::getProperty("descriptionvalidation");
		}

		// Convert to a JSON string
		public override function toString():String
		{
			// Create a JSON response string that will be recognized by the server
			var sReagentJSON:String = "{";
			sReagentJSON += JSONDataString("type", Type);
			sReagentJSON += JSONDataObject("available", Available);
			sReagentJSON += JSONDataObject("reagentid", ReagentID);
			sReagentJSON += JSONDataObject("componentid", ComponentID);
			sReagentJSON += JSONDataString("position", Position);
			sReagentJSON += JSONDataString("name", Name);
			sReagentJSON += JSONDataString("description", Description, false);
			sReagentJSON += "}";
			return sReagentJSON;
		}

		// Reagent comparison function.  Returns true if the reagents are equal, false otherwise.
		public static function CompareReagents(pReagentA:Reagent, pReagentB:Reagent):Boolean
		{
			if (pReagentA.Available != pReagentB.Available)
			{
				return false;
			}
			if (pReagentA.ReagentID != pReagentB.ReagentID)
			{
				return false;
			}
			if (pReagentA.ComponentID != pReagentB.ComponentID)
			{
				return false;
			}
			if (pReagentA.Position != pReagentB.Position)
			{
				return false;
			}
			if (pReagentA.Name != pReagentB.Name)
			{
				return false;
			}
			if (pReagentA.Description != pReagentB.Description)
			{
				return false;
			}
			return true;
		}

		// Reagent array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareReagentArrays(pReagentsA:Array, pReagentsB:Array):Boolean
		{
			if (pReagentsA.length != pReagentsB.length)
			{
				return false;
			}
			else
			{
				var pReagentA:Reagent, pReagentB:Reagent;
				for (var i:int = 0; i < pReagentsA.length; ++i)
				{
					pReagentA = pReagentsA[i] as Reagent;
					pReagentB = pReagentsB[i] as Reagent;
					if (!CompareReagents(pReagentA, pReagentB))
					{
						return false;
					}
				}
			}
			return true;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"reagent\"," +
			"\"available\":false," +
			"\"reagentid\":0," +
			"\"componentid\":0," +
			"\"position\":\"\"," +
			"\"name\":\"\"," +
			"\"description\":\"\"}";
	}
}
