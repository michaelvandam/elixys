package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentTransfer extends ComponentBase
	{
		// Constructor
		public function ComponentTransfer(data:String = null, existingcontent:Object = null)
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
			return "TRANSFER";
		}
		public static function get SKINUP():Class
		{
			return tools_transfer_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_transfer_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_transfer_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_transfer_up;
		}

		// Data wrappers
		public function get SourceReactor():uint
		{
			return super.flash_proxy::getProperty("sourcereactor");
		}
		public function set SourceReactor(value:uint):void
		{
			super.flash_proxy::setProperty("sourcereactor", value);
		}

		public function get SourceReactorValidation():String
		{
			return super.flash_proxy::getProperty("sourcereactorvalidation");
		}

		public function get TargetReactor():uint
		{
			return super.flash_proxy::getProperty("targetreactor");
		}
		public function set TargetReactor(value:uint):void
		{
			super.flash_proxy::setProperty("targetreactor", value);
		}
		
		public function get TargetReactorValidation():String
		{
			return super.flash_proxy::getProperty("targetreactorvalidation");
		}

		public function get Mode():String
		{
			return super.flash_proxy::getProperty("mode");
		}
		public function set Mode(value:String):void
		{
			super.flash_proxy::setProperty("mode", value);
		}

		public function get ModeValidation():String
		{
			return super.flash_proxy::getProperty("modevalidation");
		}

		public function get Pressure():Number
		{
			return super.flash_proxy::getProperty("pressure");
		}
		public function set Pressure(value:Number):void
		{
			super.flash_proxy::setProperty("pressure", value);
		}
		
		public function get PressureValidation():String
		{
			return super.flash_proxy::getProperty("pressurevalidation");
		}

		public function get Duration():uint
		{
			return super.flash_proxy::getProperty("duration");
		}
		public function set Duration(value:uint):void
		{
			super.flash_proxy::setProperty("duration", value);
		}
		
		public function get DurationValidation():String
		{
			return super.flash_proxy::getProperty("durationvalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sTransferDetails:String = JSONDataObject("sourcereactor", SourceReactor);
			sTransferDetails += JSONDataObject("targetreactor", TargetReactor);
			sTransferDetails += JSONDataString("mode", Mode);
			sTransferDetails += JSONDataObject("pressure", Pressure);
			sTransferDetails += JSONDataObject("duration", Duration, false);
			return sTransferDetails;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"TRANSFER\"," +
			"\"id\":0," +
			"\"name\":\"Transfer\"," +
			"\"sourcereactor\":0," +
			"\"targetreactor\":0," +
			"\"mode\":\"Trap\"," +
			"\"pressure\":0," +
			"\"duration\":0}";
	}
}
