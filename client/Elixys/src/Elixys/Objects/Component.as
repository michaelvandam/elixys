package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class Component extends JSONObject
	{
		// Constructor
		public function Component(data:String = null, existingcontent:Object = null)
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
		public function set Type(value:String):void
		{
			super.flash_proxy::setProperty("type", value);
		}
		
		public function get ComponentType():String
		{
			return super.flash_proxy::getProperty("componenttype");
		}
		public function set ComponentType(value:String):void
		{
			super.flash_proxy::setProperty("componenttype", value);
		}

		public function get ID():uint
		{
			return parseInt(super.flash_proxy::getProperty("id"));
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}
		
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get ValidationError():Boolean
		{
			return super.flash_proxy::getProperty("validationerror");
		}
		public function set ValidationError(value:Boolean):void
		{
			super.flash_proxy::setProperty("validationerror", value);
		}
		
		// Overridden by derived classes to format additional component details
		protected function FormatComponentDetails():String
		{
			return "";
		}

		// Convert to a JSON string
		public override function toString():String
		{
			// Give our derived class a chance to format additional details
			var sAdditionalDetails:String = FormatComponentDetails();
			
			// Create a JSON response string that will be recognized by the server
			var sJSON:String = "{";
			sJSON += JSONDataString("type", Type);
			sJSON += JSONDataString("componenttype", ComponentType);
			sJSON += JSONDataString("name", Name);
			sJSON += JSONDataObject("id", ID, sAdditionalDetails != "");
			if (sAdditionalDetails != "")
			{
				sJSON += sAdditionalDetails;
			}
			sJSON += "}";
			return sJSON;
		}
		
		// Type
		static public var TYPE:String = "component";
	}
}
