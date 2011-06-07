package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentComment extends Component
	{
		// Constructor
		public function ComponentComment(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Comment():String
		{
			return super.flash_proxy::getProperty("comment");
		}
		public function set Comment(value:String):void
		{
			super.flash_proxy::setProperty("comment", value);
		}
		
		public function get CommentDescription():String
		{
			return super.flash_proxy::getProperty("commentdescription");
		}
		public function set CommentDescription(value:String):void
		{
			super.flash_proxy::setProperty("commentdescription", value);
		}
		
		public function get CommentValidation():String
		{
			return super.flash_proxy::getProperty("commentvalidation");
		}
		public function set CommentValidation(value:String):void
		{
			super.flash_proxy::setProperty("commentvalidation", value);
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataString("comment", Comment, false);
		}

		// Type
		static public var TYPE:String = "COMMENT";

		// Default format
		private var m_sDefault:String = "{ \"type\":\"component\", \"componenttype\":\"COMMENT\", \"name\":\"\", \"componentid\":\"\", " +
			"\"sequenceid\":\"\", \"reactor\":\"\", \"reactordescription\":\"\", \"reactorvalidation\":\"\", \"comment\":\"\", " +
			"\"commentdescription\":\"\", \"commentvalidation\":\"\" }";
	}
}
