package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class Reagent extends JSONObject
	{
		// Constructor
		public function Reagent(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		/// Copy
		public function Copy(pSourceReagent:Reagent):void
		{
			Used = pSourceReagent.Used;
			ComponentID = pSourceReagent.ComponentID;
			Position = pSourceReagent.Position;
			Name = pSourceReagent.Name;
			NameError = pSourceReagent.NameError;
			Description = pSourceReagent.Description;
			DescriptionError = pSourceReagent.DescriptionError;
			ID = pSourceReagent.ID;
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
		
		public function get Used():Boolean
		{
			return (super.flash_proxy::getProperty("used") == "true");
		}
		public function set Used(value:Boolean):void
		{
			super.flash_proxy::setProperty("used", value ? "true" : "false");
		}

		public function get ComponentID():String
		{
			return super.flash_proxy::getProperty("componentid");
		}
		public function set ComponentID(value:String):void
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

		public function get NameError():String
		{
			return super.flash_proxy::getProperty("nameerror");
		}
		public function set NameError(value:String):void
		{
			super.flash_proxy::setProperty("nameerror", value);
		}

		public function get Description():String
		{
			return super.flash_proxy::getProperty("description");
		}
		public function set Description(value:String):void
		{
			super.flash_proxy::setProperty("description", value);
		}

		public function get DescriptionError():String
		{
			return super.flash_proxy::getProperty("descriptionerror");
		}
		public function set DescriptionError(value:String):void
		{
			super.flash_proxy::setProperty("descriptionerror", value);
		}

		public function get ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
		public function set ID(value:String):void
		{
			super.flash_proxy::setProperty("id", value);
		}

		// Type
		static public var TYPE:String = "reagent";
		
		// Default format
		private var m_sDefault:String = "{ \"type\":\"reagent\", \"used\":\"\", \"componentid\":\"\", \"position\":\"\", " +
			"\"name\":\"\", \"nameerror\":\"\", \"description\":\"\", \"descriptionerror\":\"\", \"id\":\"\" }";
	}
}
