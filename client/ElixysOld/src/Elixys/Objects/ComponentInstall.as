package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentInstall extends Component
	{
		// Constructor
		public function ComponentInstall(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}

		public function get Message():String
		{
			return super.flash_proxy::getProperty("message");
		}
		public function set Message(value:String):void
		{
			super.flash_proxy::setProperty("message", value);
		}
		
		public function get MessageValidation():String
		{
			return super.flash_proxy::getProperty("messagevalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sInstallDetails:String = JSONDataObject("reactor", Reactor);
			sInstallDetails += JSONDataString("message", Message, false);
			return sInstallDetails;
		}

		// Type
		static public var TYPE:String = "INSTALL";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"INSTALL\"," +
			"\"id\":0," +
			"\"name\":\"Install\"," +
			"\"reactor\":0," +
			"\"message\":\"\"}";
	}
}
