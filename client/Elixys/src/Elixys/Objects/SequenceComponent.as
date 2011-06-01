package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class SequenceComponent extends JSONObject
	{
		// Constructor
		public function SequenceComponent(data:String = null, existingcontent:Object = null)
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
		public function Copy(pSourceComponent:SequenceComponent):void
		{
			Name = pSourceComponent.Name;
			ID = pSourceComponent.ID;
			ComponentType = pSourceComponent.ComponentType;
			ValidationError = pSourceComponent.ValidationError;
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
		
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get ID():uint
		{
			return parseInt(super.flash_proxy::getProperty("id"));
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}

		public function get ComponentType():String
		{
			return super.flash_proxy::getProperty("componenttype");
		}
		public function set ComponentType(value:String):void
		{
			super.flash_proxy::setProperty("componenttype", value);
		}

		public function get ValidationError():Boolean
		{
			return (super.flash_proxy::getProperty("validationerror") == "true");
		}
		public function set ValidationError(value:Boolean):void
		{
			super.flash_proxy::setProperty("validationerror", value ? "true" : "false");
		}

		public function get DisplayIndex():uint
		{
			return m_nDisplayIndex;
		}
		public function set DisplayIndex(value:uint):void
		{
			m_nDisplayIndex = value;
		}

		// Type
		static public var TYPE:String = "sequencecomponent";
		
		// Default format
		private var m_sDefault:String = "{ \"type\":\"sequencecomponent\", \"name\":\"\", \"id\":\"\", \"componenttype\":\"\", " +
			"\"validationerror\":\"\" }";
		
		// Component index for displaying
		private var m_nDisplayIndex:uint = 0;
	}
}
