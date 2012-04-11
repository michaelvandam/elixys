package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentInstall extends ComponentBase
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
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "INSTALL";
		}
		public static function get SKINUP():Class
		{
			return tools_install_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_install_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_install_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_install_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 2;
		public static var FIELDLABELS:Array = [
			"REACTOR", 
			"MESSAGE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_MULTILINEINPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			""
		];
		public static var FIELDPROPERTIES:Array = [
			"Reactor", 
			"Message"
		];
		
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
			return unescape(super.flash_proxy::getProperty("message"));
		}
		public function set Message(value:String):void
		{
			super.flash_proxy::setProperty("message", escape(value));
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

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentInstallA:ComponentInstall = new ComponentInstall(null, pComponentA);
			var pComponentInstallB:ComponentInstall = new ComponentInstall(null, pComponentB);
			if (pComponentInstallA.Reactor != pComponentInstallB.Reactor)
			{
				return false;
			}
			if (pComponentInstallA.Message != pComponentInstallB.Message)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sReactorError = ValidateField(Reactor, ReactorValidation);
			m_sMessageError = ValidateField(Message, MessageValidation);
		}
		
		// Validation fields
		public function get ReactorError():String
		{
			return m_sReactorError;
		}
		public function get MessageError():String
		{
			return m_sMessageError;
		}
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"INSTALL\"," +
			"\"id\":0," +
			"\"name\":\"Install\"," +
			"\"reactor\":0," +
			"\"message\":\"\"}";
		
		// Validation error
		protected var m_sReactorError:String = "";
		protected var m_sMessageError:String = "";
	}
}
